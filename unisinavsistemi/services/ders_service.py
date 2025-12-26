from db.connection import get_connection

def ders_ekle(ad, bolum_id, ogretim_uyesi_id, ogrenci_sayisi, sinav_suresi, sinav_turu, sinav_var_mi=True):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO ders (ad, bolum_id, ogretim_uyesi_id, ogrenci_sayisi, sinav_suresi, sinav_turu, sinav_var_mi)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        ad,
        bolum_id,
        ogretim_uyesi_id,
        ogrenci_sayisi,
        sinav_suresi,
        sinav_turu,
        int(sinav_var_mi)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def ders_listele():
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT
            d.id,
            d.ad AS ders_adi,
            b.ad AS bolum_adi,
            f.ad AS fakulte_adi,
            o.ad_soyad AS ogretim_uyesi,
            d.ogrenci_sayisi,
            d.sinav_suresi,
            d.sinav_turu,
            d.sinav_var_mi
        FROM ders d
        JOIN bolum b ON d.bolum_id = b.id
        JOIN fakulte f ON b.fakulte_id = f.id
        JOIN ogretim_uyesi o ON d.ogretim_uyesi_id = o.id
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def ders_sil(ders_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM ders WHERE id = %s"
    cursor.execute(sql, (ders_id,))
    conn.commit()
    cursor.close()
    conn.close()
