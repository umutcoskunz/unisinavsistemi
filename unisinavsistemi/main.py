#öğrenci:230101001@kocaelisaglik.edu.tr    12345678901
#bolumyetkilisi:bm_yet@kocaelisaglik.edu.tr   12345678901
#hoca:poyraz.karayel@kocaelisaglik.edu.tr   12345678901

import tkinter as tk
from tkinter import ttk, messagebox

from services.kullanici_service import kullanici_dogrula
from gui import (
    build_admin_gui,
    build_bolum_yetkilisi_gui,
    build_hoca_gui,
    build_ogrenci_gui,
)


def ac_gui_kullanici_icin(user_dict):
    """
    Login doğrulandıktan sonra, kullanıcının rolüne göre
    ilgili arayüzü açar.
    """
    rol = user_dict.get("rol")

    if rol == "admin":
        build_admin_gui(user_dict)
    elif rol == "bolum_yetkilisi":
        build_bolum_yetkilisi_gui(user_dict)
    elif rol == "hoca":
        build_hoca_gui(user_dict)
    elif rol == "ogrenci":
        build_ogrenci_gui(user_dict)
    else:
        # Buraya normalde düşmemesi lazım, ama düşerse konsola yazsın.
        print(f"Bilinmeyen rol: {rol}")


def main():
    # --- GİRİŞ PENCERESİ ---
    root = tk.Tk()
    root.title("Üniversite Sınav Sistemi - Giriş")
    root.geometry("420x230")
    root.resizable(False, False)

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(
        main_frame,
        text="Üniversite Sınav Planlama Sistemi",
        font=("Segoe UI", 12, "bold"),
    ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

    ttk.Label(main_frame, text="Kullanıcı Adı (mail):").grid(
        row=1, column=0, sticky="w", pady=5
    )
    entry_user = ttk.Entry(main_frame, width=35)
    entry_user.grid(row=1, column=1, pady=5)

    ttk.Label(main_frame, text="Şifre:").grid(
        row=2, column=0, sticky="w", pady=5
    )
    entry_pass = ttk.Entry(main_frame, width=35, show="*")
    entry_pass.grid(row=2, column=1, pady=5)

    # Örnek bilgilendirme (istersen silebilirsin)
    info_label = ttk.Label(
        main_frame,
        
        foreground="gray",
        justify="left",
    )
    info_label.grid(row=3, column=0, columnspan=2, pady=(5, 10), sticky="w")

    def try_login(event=None):
        kullanici_adi = entry_user.get().strip()
        sifre = entry_pass.get().strip()

        if not kullanici_adi or not sifre:
            messagebox.showwarning(
                "Uyarı", "Kullanıcı adı ve şifre boş olamaz."
            )
            return

        user = kullanici_dogrula(kullanici_adi, sifre)
        if not user:
            messagebox.showerror(
                "Hata", "Kullanıcı adı veya şifre hatalı."
            )
            return

        # Giriş başarılı, login penceresini kapatıp rol bazlı GUI açıyoruz
        root.destroy()
        ac_gui_kullanici_icin(user)

    btn_login = ttk.Button(main_frame, text="Giriş Yap", command=try_login)
    btn_login.grid(row=4, column=1, sticky="e", pady=5)

    # Enter'a basınca da login olsun
    root.bind("<Return>", try_login)

    root.mainloop()


if __name__ == "__main__":
    main()
