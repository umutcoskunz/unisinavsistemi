from db.connection import get_connection

def ozel_durum_ekle(ogretim_uyesi_id, tarih, baslangic_saat, bitis_saat, aciklama):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO ozel_durum (ogretim_uyesi_id, tarih, baslangic_saat, bitis_saat, aciklama)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (ogretim_uyesi_id, tarih, baslangic_saat, bitis_saat, aciklama))
    conn.commit()
    cursor.close()
    conn.close()

def ozel_durum_listele():
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT
            z.id,
            o.ad_soyad,
            z.tarih,
            z.baslangic_saat,
            z.bitis_saat,
            z.aciklama
        FROM ozel_durum z
        JOIN ogretim_uyesi o ON z.ogretim_uyesi_id = o.id
        ORDER BY z.tarih, z.baslangic_saat
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def ozel_durum_sil(ozel_durum_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM ozel_durum WHERE id = %s"
    cursor.execute(sql, (ozel_durum_id,))
    conn.commit()
    cursor.close()
    conn.close()
