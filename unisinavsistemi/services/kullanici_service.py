from db.connection import get_connection


def kullanici_ekle(kullanici_adi, sifre, rol, bolum_id=None, ogretim_uyesi_id=None):
    """
    Yeni kullanıcı ekler.
    - kullanici_adi: mail (örn: 230101023@kocaelisaglik.edu.tr)
    - sifre: TCKN gibi string
    - rol: 'admin' / 'bolum_yetkilisi' / 'hoca' / 'ogrenci'
    - bolum_id: öğrenci veya bölüm yetkilisi için (int ya da None)
    - ogretim_uyesi_id: hoca için (int ya da None)
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO kullanici (kullanici_adi, sifre, rol, bolum_id, ogretim_uyesi_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (kullanici_adi, sifre, rol, bolum_id, ogretim_uyesi_id))

    conn.commit()
    cursor.close()
    conn.close()


def kullanici_listele():
    """
    Tüm kullanıcıları döner.
    GUI tarafında rahat kullanmak için dict olarak dönüyoruz.
    [
      {"id": 1, "kullanici_adi": "...", "rol": "...", "bolum_id": 1, "ogretim_uyesi_id": None},
      ...
    ]
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, kullanici_adi, sifre, rol, bolum_id, ogretim_uyesi_id
        FROM kullanici
        ORDER BY id
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def kullanici_sil(kullanici_id: int):
    """
    ID'ye göre kullanıcı siler.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM kullanici WHERE id = %s", (kullanici_id,))

    conn.commit()
    cursor.close()
    conn.close()


def kullanici_dogrula(kullanici_adi: str, sifre: str):
    """
    Login ekranı için:
      - doğruysa kullanıcı kaydını (dict) döner
      - yanlışsa None döner
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT id, kullanici_adi, rol, bolum_id, ogretim_uyesi_id
        FROM kullanici
        WHERE kullanici_adi = %s AND sifre = %s
        LIMIT 1
    """
    cursor.execute(sql, (kullanici_adi, sifre))
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return row
