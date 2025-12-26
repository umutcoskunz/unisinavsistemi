from db.connection import get_connection
import datetime


# ------------------------------------------------------------
# Yardımcı: TIME tipini datetime.time'a çevir
# ------------------------------------------------------------
def _to_time(value) -> datetime.time | None:
    """
    MySQL TIME tipleri farklı şekillerde gelebiliyor:
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
        hh_mm = s[:5]  # '09:01' gibi
        h, m = hh_mm.split(":")
        return datetime.time(int(h), int(m))
    except Exception:
        return None


# ============================================================
# YARDIMCI: BU DERSE ZATEN SINAV VAR MI?
# ============================================================
def sinav_mevcut_mu(ders_id: int) -> bool:
    """
    Verilen ders_id için sinav tablosunda kayıt var mı?
    Varsa True, yoksa False döner.
    """
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM sinav WHERE ders_id = %s"
    cursor.execute(sql, (ders_id,))
    (adet,) = cursor.fetchone()
    cursor.close()
    conn.close()
    return adet > 0


# ============================================================
# SINAV EKLE  (çatışma + doğrulama kontrolü)
# ============================================================
def sinav_ekle(ders_id, tarih, saat, derslik_id):
    """
    Kurallar:
      - Aynı derse ikinci kez sınav atanamaz
      - Aynı derslikte, sınav süresi boyunca başka sınav olamaz
      - Tarih ve saat formatları kontrol edilir
    Hata durumlarında Türkçe ValueError fırlatılır.
    """

    # ---------- 0) Giriş doğrulama ----------
    if not tarih:
        raise ValueError("Tarih boş bırakılamaz. (Örn: 2025-01-06)")

    # tarih formatı
    try:
        datetime.date.fromisoformat(str(tarih))
    except Exception:
        raise ValueError(
            "Tarih formatı hatalı.\n"
            "Lütfen YYYY-AA-GG formatında giriniz. (Örn: 2025-01-06)"
        )

    if not saat:
        raise ValueError(
            "Saat boş bırakılamaz.\n"
            "Lütfen HH:MM formatında giriniz. (Örn: 09:00)"
        )

    t_saat = _to_time(saat)
    if t_saat is None:
        raise ValueError(
            "Saat formatı hatalı.\n"
            "Lütfen HH:MM formatında giriniz. (Örn: 09:00 veya 13:30)"
        )

    # ---------- 1) Aynı derse daha önce sınav atanmış mı? ----------
    if sinav_mevcut_mu(ders_id):
        raise ValueError(
            "Bu derse zaten bir sınav atanmış.\n"
            "Aynı derse ikinci bir sınav ekleyemezsiniz."
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ---------- 2) Bu dersin sınav süresini al ----------
    cursor.execute(
        "SELECT sinav_suresi FROM ders WHERE id = %s",
        (ders_id,),
    )
    ders_kaydi = cursor.fetchone()
    if not ders_kaydi:
        cursor.close()
        conn.close()
        raise ValueError("Geçersiz ders ID. Böyle bir ders bulunamadı.")

    yeni_sure = int(ders_kaydi["sinav_suresi"])

    bugun = datetime.date.today()
    yeni_bas = datetime.datetime.combine(bugun, t_saat)
    yeni_bit = yeni_bas + datetime.timedelta(minutes=yeni_sure)

    # ---------- 3) Aynı derslikte aynı gün başka sınav var mı? ----------
    cursor.execute(
        """
        SELECT s.tarih, s.saat, d.sinav_suresi,
               d.ad AS ders_ad
        FROM sinav s
        JOIN ders d ON s.ders_id = d.id
        WHERE s.derslik_id = %s
          AND s.tarih = %s
        """,
        (derslik_id, tarih),
    )
    mevcutlar = cursor.fetchall()

    for rec in mevcutlar:
        var_saat = rec["saat"]
        var_sure = int(rec["sinav_suresi"])

        var_t = _to_time(var_saat)
        if var_t is None:
            # Veritabanında bozuk bir saat görürsek daha açıklayıcı mesaj verelim
            cursor.close()
            conn.close()
            raise ValueError(
                "Veritabanında geçersiz saat bilgisi tespit edildi.\n"
                "Lütfen mevcut sınav kayıtlarını kontrol edin."
            )

        var_bas = datetime.datetime.combine(bugun, var_t)
        var_bit = var_bas + datetime.timedelta(minutes=var_sure)

        # zaman aralığı çakışma kontrolü
        # [yeni_bas, yeni_bit) ile [var_bas, var_bit) kesişiyor mu?
        if not (yeni_bit <= var_bas or yeni_bas >= var_bit):
            cursor.close()
            conn.close()
            raise ValueError(
                "Bu derslik, seçtiğiniz tarih ve saatte başka bir sınav için kullanılıyor.\n"
                "Lütfen farklı bir saat veya derslik seçin."
            )

    cursor.close()

    # ---------- 4) Her şey yolunda → sınavı ekle ----------
    cursor = conn.cursor()
    sql_insert = """
        INSERT INTO sinav (ders_id, tarih, saat, derslik_id)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql_insert, (ders_id, tarih, saat, derslik_id))
    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# ROLE-BAZLI FİLTRE DESTEKLEYEN SINAV LİSTELE
# ============================================================
# Kullanım:
#   sinav_listele() → Admin: tüm sınavlar
#   sinav_listele(bolum_id=2) → Bölüm yetkilisi / öğrenci (kendi bölümü)
#   sinav_listele(ogretim_uyesi_id=5) → Hoca kendi sınavları
#   sinav_listele(bolum_id=2, diger_bolumler=True) → 2 dışındaki bölümler
# ============================================================
def sinav_listele(bolum_id=None, ogretim_uyesi_id=None, diger_bolumler=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            s.id,
            d.ad AS ders_ad,
            b.ad AS bolum_ad,
            f.ad AS fakulte_ad,
            ou.ad_soyad AS hoca_ad,
            dl.ad AS derslik_ad,
            s.tarih,
            s.saat
        FROM sinav s
        JOIN ders d           ON s.ders_id = d.id
        JOIN bolum b          ON d.bolum_id = b.id
        JOIN fakulte f        ON b.fakulte_id = f.id
        JOIN ogretim_uyesi ou ON d.ogretim_uyesi_id = ou.id
        JOIN derslik dl       ON s.derslik_id = dl.id
    """

    where_clauses = []
    params = []

    # Bölüm filtrelemesi
    if bolum_id is not None:
        if diger_bolumler:
            where_clauses.append("b.id <> %s")
        else:
            where_clauses.append("b.id = %s")
        params.append(bolum_id)

    # Hoca filtrelemesi
    if ogretim_uyesi_id is not None:
        where_clauses.append("ou.id = %s")
        params.append(ogretim_uyesi_id)

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " ORDER BY s.tarih, s.saat"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ============================================================
# SINAV SİL
# ============================================================
def sinav_sil(sinav_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM sinav WHERE id = %s"
    cursor.execute(sql, (sinav_id,))
    conn.commit()
    cursor.close()
    conn.close()
