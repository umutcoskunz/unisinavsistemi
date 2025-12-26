from db.connection import get_connection

def bolum_ekle(ad, fakulte_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO bolum (ad, fakulte_id) VALUES (%s, %s)"
    cursor.execute(sql, (ad, fakulte_id))
    conn.commit()
    cursor.close()
    conn.close()

def bolum_listele():
    conn = get_connection()
    cursor = conn.cursor()
    # Fakülte adını da göstermek için JOIN kullanalım
    sql = """
        SELECT b.id, b.ad, f.ad AS fakulte_adi
        FROM bolum b
        JOIN fakulte f ON b.fakulte_id = f.id
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def bolum_sil(bolum_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM bolum WHERE id = %s"
    cursor.execute(sql, (bolum_id,))
    conn.commit()
    cursor.close()
    conn.close()
