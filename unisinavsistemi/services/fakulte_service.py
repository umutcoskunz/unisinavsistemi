from db.connection import get_connection

def fakulte_ekle(ad):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO fakulte (ad) VALUES (%s)"
    cursor.execute(sql, (ad,))
    conn.commit()
    cursor.close()
    conn.close()

def fakulte_listele():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad FROM fakulte")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fakulte_sil(fakulte_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM fakulte WHERE id = %s"
    cursor.execute(sql, (fakulte_id,))
    conn.commit()
    cursor.close()
    conn.close()
