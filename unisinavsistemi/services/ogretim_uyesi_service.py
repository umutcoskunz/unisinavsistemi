from db.connection import get_connection

def ogretim_uyesi_ekle(ad_soyad, bolum_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO ogretim_uyesi (ad_soyad, bolum_id) VALUES (%s, %s)"
    cursor.execute(sql, (ad_soyad, bolum_id))
    conn.commit()
    cursor.close()
    conn.close()

def ogretim_uyesi_listele():
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT o.id, o.ad_soyad, b.ad AS bolum_adi
        FROM ogretim_uyesi o
        JOIN bolum b ON o.bolum_id = b.id
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def ogretim_uyesi_sil(ogretim_uyesi_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM ogretim_uyesi WHERE id = %s"
    cursor.execute(sql, (ogretim_uyesi_id,))
    conn.commit()
    cursor.close()
    conn.close()
