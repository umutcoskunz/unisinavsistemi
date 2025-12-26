from db.connection import get_connection


def hoca_musaitlik_ekle(ogretim_uyesi_id, gun, baslangic_saat, bitis_saat, aciklama):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO hoca_musaitlik (ogretim_uyesi_id, gun, baslangic_saat, bitis_saat, aciklama)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (ogretim_uyesi_id, gun, baslangic_saat, bitis_saat, aciklama))
    conn.commit()
    cursor.close()
    conn.close()


def hoca_musaitlik_listele():
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT
            h.id,
            o.ad_soyad,
            h.gun,
            h.baslangic_saat,
            h.bitis_saat,
            h.aciklama
        FROM hoca_musaitlik h
        JOIN ogretim_uyesi o ON h.ogretim_uyesi_id = o.id
        ORDER BY o.ad_soyad, h.gun, h.baslangic_saat
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def hoca_musaitlik_sil(musaitlik_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM hoca_musaitlik WHERE id = %s"
    cursor.execute(sql, (musaitlik_id,))
    conn.commit()
    cursor.close()
    conn.close()
