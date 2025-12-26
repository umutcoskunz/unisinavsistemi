from db.connection import get_connection

def derslik_ekle(ad, kapasite, uygun_mu=True):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO derslik (ad, kapasite, uygun_mu) VALUES (%s, %s, %s)"
    cursor.execute(sql, (ad, kapasite, int(uygun_mu)))
    conn.commit()
    cursor.close()
    conn.close()

def derslik_listele():
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT id, ad, kapasite, uygun_mu FROM derslik"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def derslik_sil(derslik_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM derslik WHERE id = %s"
    cursor.execute(sql, (derslik_id,))
    conn.commit()
    cursor.close()
    conn.close()
