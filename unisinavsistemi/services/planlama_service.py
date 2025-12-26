from db.connection import get_connection
from services.sinav_service import sinav_ekle
from services.ozel_durum_service import ozel_durum_listele
import datetime
import re


def _to_time(value) -> datetime.time | None:
    """
    MySQL'den gelen saat değeri şu tiplerde olabilir:
      - '10:00'
      - '10:00:00'
      - datetime.time
      - datetime.timedelta
    Hepsini datetime.time'a çevirmeye çalışıyoruz.
    """
    if value is None:
        return None

    if isinstance(value, datetime.time):
        return value

    if isinstance(value, datetime.timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return datetime.time(hours, minutes)

    s = str(value).strip()
    try:
        hh_mm = s[:5]  # '10:00'
        h, m = hh_mm.split(":")
        return datetime.time(int(h), int(m))
    except Exception:
        return None


def _dakika_farki(baslangic, bitis) -> int:
    """
    İki saat değeri (string/time/timedelta) arasındaki farkı dakika cinsinden döndürür.
    """
    t1 = _to_time(baslangic)
    t2 = _to_time(bitis)
    if t1 is None or t2 is None:
        return 0

    dt1 = datetime.datetime.combine(datetime.date.today(), t1)
    dt2 = datetime.datetime.combine(datetime.date.today(), t2)
    return int((dt2 - dt1).total_seconds() // 60)


def _slot_ozel_duruma_cakisir_mi(hoca_id, tarih, saat, ozel_durum_harita):
    """
    Verilen (hoca_id, tarih, saat) için hoca o anda özel durumda mı?
    True dönerse bu slot KULLANILMAMALI.
    """
    kayitlar = ozel_durum_harita.get(hoca_id, [])
    t_saat = _to_time(saat)
    if t_saat is None:
        return False

    for z in kayitlar:
        if str(z["tarih"]) != str(tarih):
            continue

        bas = _to_time(z["baslangic_saat"])
        bit = _to_time(z["bitis_saat"])
        if bas is None or bit is None:
            continue

        dt_t = datetime.datetime.combine(datetime.date.today(), t_saat)
        dt_bas = datetime.datetime.combine(datetime.date.today(), bas)
        dt_bit = datetime.datetime.combine(datetime.date.today(), bit)

        if dt_bas <= dt_t < dt_bit:
            return True

    return False


def _gunu_tarihe_cevir(gun_degeri) -> str | None:
    """
    hoca_musaitlik.gun alanını sinav.tarih için DATE string'e çevirir.

    Sen şu şekilde veri girebilirsin:
      - 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'
      - veya direkt '2025-01-10' gibi tarih

    Eğer zaten 'YYYY-MM-DD' formatında ise olduğu gibi döner.
    Değilse sabit bir haftaya map eder:
      Pazartesi  -> 2025-01-06
      Salı       -> 2025-01-07
      Çarşamba   -> 2025-01-08
      Perşembe   -> 2025-01-09
      Cuma       -> 2025-01-10
      Cumartesi  -> 2025-01-11
      Pazar      -> 2025-01-12
    """
    if gun_degeri is None:
        return None

    s = str(gun_degeri).strip()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s

    lower = s.lower()

    mapping = {
        "pazartesi": "2025-01-06",
        "salı": "2025-01-07",
        "sali": "2025-01-07",
        "çarşamba": "2025-01-08",
        "carsamba": "2025-01-08",
        "perşembe": "2025-01-09",
        "persembe": "2025-01-09",
        "cuma": "2025-01-10",
        "cumartesi": "2025-01-11",
        "pazar": "2025-01-12",
    }

    return mapping.get(lower, None)


def otomatik_planla():
    """
    GREEDY sınav planlama algoritması.

    Ekstra özellikler:
      - Öğrenci bazlı çakışma kontrolü
      - Kapasite yetmezse bir dersi birden fazla dersliğe bölebilme
      - Ayrıntılı geri bildirim (yerleşti / yerleşemedi, derslik birleştirildi mi, neden yerleşmedi vs.)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Sınav yapılacak dersler + ders / hoca isimleri
    cursor.execute("""
        SELECT d.id,
               d.ad AS ders_ad,
               d.ogretim_uyesi_id,
               d.ogrenci_sayisi,
               d.sinav_suresi,
               ou.ad_soyad AS hoca_ad
        FROM ders d
        JOIN ogretim_uyesi ou ON d.ogretim_uyesi_id = ou.id
        WHERE d.sinav_var_mi = 1
    """)
    dersler = cursor.fetchall()

    if not dersler:
        conn.close()
        return []

    # 2) Zaten sınavı atanmış dersleri listeden çıkar
    cursor.execute("SELECT DISTINCT ders_id FROM sinav")
    mevcut_sinav_dersleri = {row["ders_id"] for row in cursor.fetchall()}

    dersler = [d for d in dersler if d["id"] not in mevcut_sinav_dersleri]

    if not dersler:
        conn.close()
        return []

    # 3) GREEDY: öğrenci sayısına göre sırala (büyükten küçüğe)
    dersler.sort(key=lambda d: d["ogrenci_sayisi"], reverse=True)

    # 4) Uygun derslikler (ad + kapasite ile al)
    cursor.execute("""
        SELECT id, ad, kapasite
        FROM derslik
        WHERE uygun_mu = 1
    """)
    derslikler = cursor.fetchall()
    # ID -> kayıt map (kolay isim bulmak için)
    derslik_map = {d["id"]: d for d in derslikler}

    # 5) Hoca müsaitlikleri
    cursor.execute("""
        SELECT ogretim_uyesi_id, gun, baslangic_saat, bitis_saat
        FROM hoca_musaitlik
    """)
    musaitlik_kayitlari = cursor.fetchall()

    musaitlik_harita = {}
    for kayit in musaitlik_kayitlari:
        hoca_id = kayit["ogretim_uyesi_id"]
        musaitlik_harita.setdefault(hoca_id, []).append(kayit)

    # 5.5) Özel durumlar
    ozel_kayitlar = ozel_durum_listele()
    ozel_durum_harita = {}
    for z in ozel_kayitlar:
        h_id = z["ogretim_uyesi_id"]
        ozel_durum_harita.setdefault(h_id, []).append(z)

    # 6) Ders–öğrenci ilişkileri (öğrenci çakışması için)
    cursor.execute("""
        SELECT od.ders_id, od.ogrenci_id
        FROM ogrenci_ders od
    """)
    ders_ogrencileri = {}
    for row in cursor.fetchall():
        d_id = row["ders_id"]
        o_id = row["ogrenci_id"]
        ders_ogrencileri.setdefault(d_id, set()).add(o_id)

    # 7) Mevcut sınavlar → oda / hoca / öğrenci doluluk set'leri
    cursor.execute("""
        SELECT s.tarih, s.saat, s.derslik_id, d.ogretim_uyesi_id
        FROM sinav s
        JOIN ders d ON s.ders_id = d.id
    """)
    mevcut_sinavlar = cursor.fetchall()

    oda_doluluk = set()
    hoca_doluluk = set()
    for s in mevcut_sinavlar:
        oda_doluluk.add((s["tarih"], s["saat"], s["derslik_id"]))
        hoca_doluluk.add((s["tarih"], s["saat"], s["ogretim_uyesi_id"]))

    # Öğrenci doluluk
    cursor.execute("""
        SELECT s.tarih, s.saat, od.ogrenci_id
        FROM sinav s
        JOIN ogrenci_ders od ON s.ders_id = od.ders_id
    """)
    ogrenci_doluluk = set()
    for row in cursor.fetchall():
        ogrenci_doluluk.add((row["tarih"], row["saat"], row["ogrenci_id"]))

    atananlar = []

    # 8) Her dersi sırayla yerleştir
    for ders in dersler:
        ders_id = ders["id"]
        ders_ad = ders["ders_ad"]
        hoca_id = ders["ogretim_uyesi_id"]
        hoca_ad = ders["hoca_ad"]
        ogrenci_sayisi = ders["ogrenci_sayisi"]
        sinav_suresi = ders["sinav_suresi"]

        musait_listesi = musaitlik_harita.get(hoca_id, [])
        ogrenciler = ders_ogrencileri.get(ders_id, set())

        yerlestirildi = False
        nedenler = set()  # yerleşememe nedenleri (bilgi için)

        if not musait_listesi:
            nedenler.add("Hocaya tanımlı hiçbir müsaitlik bulunmuyor.")

        for m in musait_listesi:
            gun = m["gun"]
            baslangic = m["baslangic_saat"]
            bitis = m["bitis_saat"]

            tarih = _gunu_tarihe_cevir(gun)
            if tarih is None:
                nedenler.add(
                    "Hoca müsaitlik kaydındaki gün/tarih bilgisi çözümlenemedi."
                )
                continue

            fark = _dakika_farki(baslangic, bitis)
            if fark < sinav_suresi:
                nedenler.add(
                    "Hoca müsaitlik saat aralığı bu dersin sınav süresi için yetersiz."
                )
                continue

            saat = baslangic  # slot başlangıç saati

            # 1) Hoca çakışıyor mu?
            if (tarih, saat, hoca_id) in hoca_doluluk:
                nedenler.add(
                    "Seçilen zaman aralığında hocanın başka bir sınavı bulunuyor."
                )
                continue

            # 2) Hoca özel durumda mı?
            if _slot_ozel_duruma_cakisir_mi(hoca_id, tarih, saat, ozel_durum_harita):
                nedenler.add(
                    "Hocanın bu zaman aralığı için tanımlı özel durumu var."
                )
                continue

            # 3) Öğrenci çakışması var mı?
            if ogrenciler:
                conflict = False
                for ogr_id in ogrenciler:
                    if (tarih, saat, ogr_id) in ogrenci_doluluk:
                        conflict = True
                        break
                if conflict:
                    nedenler.add(
                        "Öğrencilerden en az biri aynı anda başka bir sınavda."
                    )
                    continue

            # 4) Bu tarih-saat için uygun derslikleri bul
            uygun_derslikler = []
            for dl in derslikler:
                derslik_id = dl["id"]
                kapasite = dl["kapasite"]

                # Bu saat aynı derslik dolu mu?
                if (tarih, saat, derslik_id) in oda_doluluk:
                    continue

                uygun_derslikler.append(dl)

            if not uygun_derslikler:
                nedenler.add(
                    "Bu zaman aralığı için uygun (boş) derslik bulunamadı."
                )
                continue

            # Önce tek derslik ile çözmeyi dene
            tek_yeter = [
                dl for dl in uygun_derslikler
                if dl["kapasite"] >= ogrenci_sayisi
            ]

            secilen_derslikler = []
            birlestirme_yapildi = False

            if tek_yeter:
                # En küçük yeterli kapasiteyi al (israfı azaltmak için)
                tek_yeter.sort(key=lambda d: d["kapasite"])
                secilen_derslikler = [tek_yeter[0]]
            else:
                # Kapasite yetmedi, birden fazla dersliği birleştirmeyi dene
                uygun_derslikler.sort(key=lambda d: d["kapasite"], reverse=True)

                kalan = ogrenci_sayisi
                secilen = []

                for dl in uygun_derslikler:
                    secilen.append(dl)
                    kalan -= dl["kapasite"]
                    if kalan <= 0:
                        break

                if kalan > 0:
                    # Tüm boş derslikleri toplasak bile kapasite yetmiyor
                    nedenler.add(
                        "Derslikler birleştirilse bile kapasite öğrenci sayısını karşılamıyor."
                    )
                    continue

                secilen_derslikler = secilen
                birlestirme_yapildi = True

            # Buraya geldiysek bu tarih-saat ve seçilen derslikler uygun
            derslik_id_listesi = []
            derslik_adlari = []
            toplam_kapasite = 0

            for dl in secilen_derslikler:
                derslik_id = dl["id"]
                derslik_id_listesi.append(derslik_id)
                derslik_adlari.append(dl["ad"])
                toplam_kapasite += dl["kapasite"]

                sinav_ekle(ders_id, tarih, saat, derslik_id)
                oda_doluluk.add((tarih, saat, derslik_id))

            # Hoca doluluğunu ekle
            hoca_doluluk.add((tarih, saat, hoca_id))

            # Öğrenci doluluğunu ekle
            for ogr_id in ogrenciler:
                ogrenci_doluluk.add((tarih, saat, ogr_id))

            # Kullanıcıya gösterilecek özet
            if birlestirme_yapildi:
                durum = "Yerleştirildi (derslik birleştirilerek)"
                aciklama = (
                    f"{tarih} tarihinde saat {saat} için "
                    f"{len(derslik_id_listesi)} derslik birleştirildi: "
                    f"{', '.join(derslik_adlari)}.\n"
                    f"Toplam kapasite: {toplam_kapasite}, "
                    f"öğrenci sayısı: {ogrenci_sayisi}.\n"
                    f"Hoca ve öğrencilerin diğer sınavları ile çakışma "
                    f"oluşturmayacak şekilde planlandı."
                )
            else:
                # Tek derslik
                dl = secilen_derslikler[0]
                durum = "Yerleştirildi"
                aciklama = (
                    f"{tarih} tarihinde saat {saat} için "
                    f"{dl['ad']} dersliğine yerleştirildi.\n"
                    f"Derslik kapasitesi: {dl['kapasite']}, "
                    f"öğrenci sayısı: {ogrenci_sayisi}.\n"
                    f"Hoca ve öğrencilerin diğer sınavları ile çakışma "
                    f"oluşturmayacak şekilde planlandı."
                )

            atananlar.append({
                "ders_id": ders_id,
                "ders_ad": ders_ad,
                "hoca_id": hoca_id,
                "hoca_ad": hoca_ad,
                "tarih": tarih,
                "saat": saat,
                "derslik_id": derslik_id_listesi,  # tek de olsa liste
                "durum": durum,
                "aciklama": aciklama,
            })

            yerlestirildi = True
            break  # hoca müsaitlik döngüsünden çık

        if not yerlestirildi:
            # Yerleştirilemedi, nedenleri raporla
            if not nedenler:
                aciklama = "Uygun tarih, saat ve derslik kombinasyonu bulunamadı."
            else:
                aciklama = "Nedenler:\n- " + "\n- ".join(sorted(nedenler))

            atananlar.append({
                "ders_id": ders_id,
                "ders_ad": ders_ad,
                "hoca_id": hoca_id,
                "hoca_ad": hoca_ad,
                "tarih": None,
                "saat": None,
                "derslik_id": None,
                "durum": "Yerleştirilemedi",
                "aciklama": aciklama,
            })

    conn.close()
    return atananlar
