import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from services.fakulte_service import fakulte_ekle, fakulte_listele, fakulte_sil
from services.bolum_service import bolum_ekle, bolum_listele, bolum_sil
from services.ogretim_uyesi_service import (
    ogretim_uyesi_ekle,
    ogretim_uyesi_listele,
    ogretim_uyesi_sil,
)
from services.derslik_service import derslik_ekle, derslik_listele, derslik_sil
from services.ders_service import ders_ekle, ders_listele, ders_sil
from services.hoca_musaitlik_service import (
    hoca_musaitlik_ekle,
    hoca_musaitlik_listele,
    hoca_musaitlik_sil,
)
from services.sinav_service import sinav_ekle, sinav_listele, sinav_sil
from services.planlama_service import otomatik_planla
from services.kullanici_service import (
    kullanici_listele,
    kullanici_ekle,
    kullanici_sil,
)

# --- Global Treeview referansları ---
fakulte_tree = None
bolum_tree = None
ogretim_tree = None
derslik_tree = None
ders_tree = None
musaitlik_tree = None
sinav_tree = None

def apply_theme(root):
    import tkinter as tk
    from tkinter import ttk

    style = ttk.Style(root)

    # ---- RENK PALETİ ----
    DARK = "#0b1e39"     # lacivert arka plan
    MID = "#102a4d"
    LIGHT = "#e8ecf5"
    WHITE = "#ffffff"

    # Daha modern görünen bir tema
    try:
        style.theme_use("clam")
    except:
        pass  # sistemde yoksa default kalsın

    # Genel font
    default_font = ("Segoe UI", 10)
    root.option_add("*Font", default_font)

    # ---- ANA ARKA PLAN ----
    root.configure(bg=DARK)

    # ---- Notebook (sekme) ----
    style.configure(
        "TNotebook",
        background=DARK,
        padding=5,
    )
    style.configure(
        "TNotebook.Tab",
        padding=(10, 5),
        background=MID,
        foreground=WHITE
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", LIGHT)],
        foreground=[("selected", "#000000")]
    )

    # ---- Frame / LabelFrame ----
    style.configure("TFrame", background=DARK)

    style.configure(
        "TLabelframe",
        background=DARK,
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=DARK,
        foreground=WHITE,
        font=("Segoe UI", 10, "bold")
    )

    # ---- Label ----
    style.configure(
        "TLabel",
        background=DARK,
        foreground=WHITE,
    )

    # ---- Butonlar ----
    style.configure(
        "TButton",
        padding=(8, 4),
        background=LIGHT,
        foreground="#000000"
    )
    style.map(
        "TButton",
        background=[("active", "#d6dff2")]
    )

        # ---- Treeview (tablolar) ----
    style.configure(
        "Treeview",
        background=MID,        # satır arka planı laciverte yakın
        fieldbackground=MID,
        foreground=WHITE,      # yazılar beyaz
        rowheight=24,
    )
    style.map(
        "Treeview",
        background=[("selected", "#1a3d73")],  # seçili satır biraz daha açık
        foreground=[("selected", WHITE)],
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=LIGHT,
        foreground="#000000",
    )
    style.map(
        "Treeview.Heading",
        background=[("active", LIGHT)]
    )





def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)


# ===================== FAKÜLTE SEKME =====================

def refresh_fakulte():
    global fakulte_tree
    clear_tree(fakulte_tree)
    for f in fakulte_listele():
        fakulte_tree.insert("", "end", values=f, tags=("darkrow",))


def create_fakulte_tab(notebook):
    global fakulte_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Fakülteler")

    form_frame = ttk.LabelFrame(frame, text="Fakülte Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Fakülte adı:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_ad = ttk.Entry(form_frame, width=30)
    entry_ad.grid(row=0, column=1, padx=5, pady=5)

    def fakulte_ekle_click():
        ad = entry_ad.get().strip()
        if not ad:
            messagebox.showwarning("Uyarı", "Fakülte adı boş olamaz.")
            return
        fakulte_ekle(ad)
        entry_ad.delete(0, tk.END)
        refresh_fakulte()
        messagebox.showinfo("Bilgi", "Fakülte eklendi.")

    ttk.Button(form_frame, text="Ekle", command=fakulte_ekle_click).grid(
        row=0, column=2, padx=5, pady=5
    )

    list_frame = ttk.LabelFrame(frame, text="Fakülteler")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "ad")
    fakulte_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=8
    )
    fakulte_tree.heading("id", text="ID")
    fakulte_tree.heading("ad", text="Fakülte Adı")
    fakulte_tree.column("id", width=60, anchor="center")
    fakulte_tree.column("ad", width=250, anchor="w")
    fakulte_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=fakulte_tree.yview
    )
    fakulte_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def fakulte_sil_click():
        selected = fakulte_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir fakülte seç.")
            return
        item = fakulte_tree.item(selected[0])
        fakulte_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {fakulte_id} fakülteyi silmek istiyor musun?"
        ):
            return
        try:
            fakulte_sil(fakulte_id)
            refresh_fakulte()
            messagebox.showinfo("Bilgi", "Fakülte silindi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Fakülte silinirken hata oluştu:\n{e}")

    btn_del = ttk.Button(
        frame, text="Seçili Fakülteyi Sil", command=fakulte_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_fakulte()


# ===================== BÖLÜM SEKME =====================

def refresh_bolum():
    global bolum_tree
    clear_tree(bolum_tree)
    for b in bolum_listele():
        bolum_tree.insert("", "end", values=b)


def create_bolum_tab(notebook):
    global bolum_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Bölümler")

    form_frame = ttk.LabelFrame(frame, text="Bölüm Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Bölüm adı:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_ad = ttk.Entry(form_frame, width=30)
    entry_ad.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Fakülte ID:").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    entry_fakulte_id = ttk.Entry(form_frame, width=10)
    entry_fakulte_id.grid(row=0, column=3, padx=5, pady=5)

    def bolum_ekle_click():
        ad = entry_ad.get().strip()
        fakulte_id_str = entry_fakulte_id.get().strip()
        if not ad or not fakulte_id_str:
            messagebox.showwarning(
                "Uyarı", "Bölüm adı ve fakülte ID boş olamaz."
            )
            return
        try:
            fakulte_id = int(fakulte_id_str)
        except ValueError:
            messagebox.showwarning("Uyarı", "Fakülte ID sayısal olmalı.")
            return

        bolum_ekle(ad, fakulte_id)
        entry_ad.delete(0, tk.END)
        entry_fakulte_id.delete(0, tk.END)
        refresh_bolum()
        messagebox.showinfo("Bilgi", "Bölüm eklendi.")

    ttk.Button(form_frame, text="Ekle", command=bolum_ekle_click).grid(
        row=0, column=4, padx=5, pady=5
    )

    list_frame = ttk.LabelFrame(frame, text="Bölümler")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "bolum_adi", "fakulte_adi")
    bolum_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=8
    )
    bolum_tree.heading("id", text="ID")
    bolum_tree.heading("bolum_adi", text="Bölüm Adı")
    bolum_tree.heading("fakulte_adi", text="Fakülte")
    bolum_tree.column("id", width=60, anchor="center")
    bolum_tree.column("bolum_adi", width=200, anchor="w")
    bolum_tree.column("fakulte_adi", width=200, anchor="w")
    bolum_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=bolum_tree.yview
    )
    bolum_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def bolum_sil_click():
        selected = bolum_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir bölüm seç.")
            return
        item = bolum_tree.item(selected[0])
        bolum_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {bolum_id} bölümü silmek istiyor musun?"
        ):
            return
        try:
            bolum_sil(bolum_id)
            refresh_bolum()
            messagebox.showinfo("Bilgi", "Bölüm silindi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Bölüm silinirken hata oluştu:\n{e}")

    btn_del = ttk.Button(
        frame, text="Seçili Bölümü Sil", command=bolum_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_bolum()


# ===================== ÖĞRETİM ÜYESİ SEKME =====================

def refresh_ogretim(bolum_id=None):
    global ogretim_tree
    clear_tree(ogretim_tree)

    # Tüm hocaları çek
    ogretim_listesi = ogretim_uyesi_listele()  # (id, ad_soyad, bolum_adi)

    # Bölüm yetkilisi için kendi bölüm adını bul
    hedef_bolum_adi = None
    if bolum_id is not None:
        from services.bolum_service import bolum_listele
        for b_id, b_ad, f_ad in bolum_listele():
            if b_id == bolum_id:
                hedef_bolum_adi = b_ad
                break

    for o in ogretim_listesi:
        ogretim_id, ad_soyad, bolum_adi = o

        # Bölüm yetkilisi ise sadece kendi bölümünün hocalarını göster
        if hedef_bolum_adi is not None and bolum_adi != hedef_bolum_adi:
            continue

        ogretim_tree.insert("", "end", values=o)



def create_ogretim_tab(notebook, bolum_id=None):
    global ogretim_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Öğretim Üyeleri")

    form_frame = ttk.LabelFrame(frame, text="Öğretim Üyesi Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Ad Soyad:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_ad_soyad = ttk.Entry(form_frame, width=30)
    entry_ad_soyad.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Bölüm ID:").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    entry_bolum_id = ttk.Entry(form_frame, width=10)
    entry_bolum_id.grid(row=0, column=3, padx=5, pady=5)

    # Bölüm yetkilisi ise bölüm ID’sini sabitle ve disabled yap
    if bolum_id is not None:
        entry_bolum_id.insert(0, str(bolum_id))
        entry_bolum_id.config(state="disabled")

    def ogretim_ekle_click():
        ad_soyad = entry_ad_soyad.get().strip()

        if bolum_id is not None:
            # Bölüm yetkilisi → bölüm ID sabit
            hedef_bolum_id = bolum_id
        else:
            bolum_id_str = entry_bolum_id.get().strip()
            if not bolum_id_str:
                messagebox.showwarning(
                    "Uyarı", "Bölüm ID boş olamaz."
                )
                return
            try:
                hedef_bolum_id = int(bolum_id_str)
            except ValueError:
                messagebox.showwarning("Uyarı", "Bölüm ID sayısal olmalı.")
                return

        if not ad_soyad:
            messagebox.showwarning(
                "Uyarı", "Ad soyad boş olamaz."
            )
            return

        ogretim_uyesi_ekle(ad_soyad, hedef_bolum_id)
        entry_ad_soyad.delete(0, tk.END)

        # Admin ise bölüm girişini de temizle
        if bolum_id is None:
            entry_bolum_id.delete(0, tk.END)

        refresh_ogretim(bolum_id)
        messagebox.showinfo("Bilgi", "Öğretim üyesi eklendi.")

    ttk.Button(form_frame, text="Ekle", command=ogretim_ekle_click).grid(
        row=0, column=4, padx=5, pady=5
    )

    list_frame = ttk.LabelFrame(frame, text="Öğretim Üyeleri")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "ad_soyad", "bolum_adi")
    ogretim_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=8
    )
    ogretim_tree.heading("id", text="ID")
    ogretim_tree.heading("ad_soyad", text="Ad Soyad")
    ogretim_tree.heading("bolum_adi", text="Bölüm")
    ogretim_tree.column("id", width=60, anchor="center")
    ogretim_tree.column("ad_soyad", width=200, anchor="w")
    ogretim_tree.column("bolum_adi", width=200, anchor="w")
    ogretim_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=ogretim_tree.yview
    )
    ogretim_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def ogretim_sil_click():
        selected = ogretim_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir öğretim üyesi seç.")
            return
        item = ogretim_tree.item(selected[0])
        ogretim_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {ogretim_id} öğretim üyesini silmek istiyor musun?"
        ):
            return
        try:
            ogretim_uyesi_sil(ogretim_id)
            refresh_ogretim(bolum_id)
            messagebox.showinfo("Bilgi", "Öğretim üyesi silindi.")
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Öğretim üyesi silinirken hata oluştu:\n{e}"
            )

    btn_del = ttk.Button(
        frame, text="Seçili Öğretim Üyesini Sil", command=ogretim_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    # İlk yükleme
    refresh_ogretim(bolum_id)


    def ogretim_sil_click():
        selected = ogretim_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir öğretim üyesi seç.")
            return
        item = ogretim_tree.item(selected[0])
        ogretim_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {ogretim_id} öğretim üyesini silmek istiyor musun?"
        ):
            return
        try:
            ogretim_uyesi_sil(ogretim_id)
            refresh_ogretim()
            messagebox.showinfo("Bilgi", "Öğretim üyesi silindi.")
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Öğretim üyesi silinirken hata oluştu:\n{e}"
            )

    btn_del = ttk.Button(
        frame, text="Seçili Öğretim Üyesini Sil", command=ogretim_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_ogretim()


# ===================== DERSLİK SEKME =====================

def refresh_derslik():
    global derslik_tree
    clear_tree(derslik_tree)
    for d in derslik_listele():
        derslik_id, ad, kapasite, uygun_mu = d
        durum = "Uygun" if uygun_mu == 1 else "Uygun değil"
        derslik_tree.insert("", "end", values=(derslik_id, ad, kapasite, durum))


def create_derslik_tab(notebook):
    global derslik_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Derslikler")

    form_frame = ttk.LabelFrame(frame, text="Derslik Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Ad:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_ad = ttk.Entry(form_frame, width=20)
    entry_ad.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Kapasite:").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    entry_kapasite = ttk.Entry(form_frame, width=10)
    entry_kapasite.grid(row=0, column=3, padx=5, pady=5)

    uygun_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        form_frame, text="Sınav için uygun", variable=uygun_var
    ).grid(row=0, column=4, padx=5, pady=5)

    def derslik_ekle_click():
        ad = entry_ad.get().strip()
        kapasite_str = entry_kapasite.get().strip()
        if not ad or not kapasite_str:
            messagebox.showwarning("Uyarı", "Ad ve kapasite boş olamaz.")
            return
        try:
            kapasite = int(kapasite_str)
        except ValueError:
            messagebox.showwarning("Uyarı", "Kapasite sayısal olmalı.")
            return

        derslik_ekle(ad, kapasite, uygun_var.get())
        entry_ad.delete(0, tk.END)
        entry_kapasite.delete(0, tk.END)
        uygun_var.set(True)
        refresh_derslik()
        messagebox.showinfo("Bilgi", "Derslik eklendi.")

    ttk.Button(form_frame, text="Ekle", command=derslik_ekle_click).grid(
        row=0, column=5, padx=5, pady=5
    )

    list_frame = ttk.LabelFrame(frame, text="Derslikler")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "ad", "kapasite", "durum")
    derslik_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=8
    )
    derslik_tree.heading("id", text="ID")
    derslik_tree.heading("ad", text="Ad")
    derslik_tree.heading("kapasite", text="Kapasite")
    derslik_tree.heading("durum", text="Durum")
    derslik_tree.column("id", width=60, anchor="center")
    derslik_tree.column("ad", width=150, anchor="w")
    derslik_tree.column("kapasite", width=80, anchor="center")
    derslik_tree.column("durum", width=100, anchor="center")
    derslik_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=derslik_tree.yview
    )
    derslik_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def derslik_sil_click():
        selected = derslik_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir derslik seç.")
            return
        item = derslik_tree.item(selected[0])
        derslik_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {derslik_id} dersliği silmek istiyor musun?"
        ):
            return
        try:
            derslik_sil(derslik_id)
            refresh_derslik()
            messagebox.showinfo("Bilgi", "Derslik silindi.")
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Derslik silinirken hata oluştu:\n{e}"
            )

    btn_del = ttk.Button(
        frame, text="Seçili Dersliği Sil", command=derslik_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_derslik()


# ===================== DERSLER SEKME =====================

def refresh_ders(bolum_id=None):
    global ders_tree
    clear_tree(ders_tree)

    dersler = ders_listele()  # tüm dersler

    # Bölüm yetkilisi için kendi bölüm adını bul
    hedef_bolum_adi = None
    if bolum_id is not None:
        from services.bolum_service import bolum_listele
        for b_id, b_ad, f_ad in bolum_listele():
            if b_id == bolum_id:
                hedef_bolum_adi = b_ad
                break

    for d in dersler:
        (
            ders_id,
            ders_adi,
            bolum_adi,
            fakulte_adi,
            ogretim_uyesi,
            ogrenci_sayisi,
            sinav_suresi,
            sinav_turu,
            sinav_var_mi,
        ) = d

        # Bölüm yetkilisi ise sadece kendi bölümünün derslerini göster
        if hedef_bolum_adi is not None and bolum_adi != hedef_bolum_adi:
            continue

        durum = "Sınav var" if sinav_var_mi == 1 else "Sınav yok"
        ders_tree.insert(
            "",
            "end",
            values=(
                ders_id,
                ders_adi,
                fakulte_adi,
                bolum_adi,
                ogretim_uyesi,
                ogrenci_sayisi,
                sinav_suresi,
                sinav_turu,
                durum,
            ),
        )



def create_ders_tab(notebook, bolum_id=None):
    global ders_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Dersler")

    form_frame = ttk.LabelFrame(frame, text="Ders Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Bölüm ID:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_bolum_id = ttk.Entry(form_frame, width=8)
    entry_bolum_id.grid(row=0, column=1, padx=5, pady=5)

    # Bölüm yetkilisi ise bölüm ID’sini sabitle
    if bolum_id is not None:
        entry_bolum_id.insert(0, str(bolum_id))
        entry_bolum_id.config(state="disabled")

    ttk.Label(form_frame, text="Hoca ID:").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    entry_hoca_id = ttk.Entry(form_frame, width=8)
    entry_hoca_id.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(form_frame, text="Ders adı:").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    entry_ders_ad = ttk.Entry(form_frame, width=25)
    entry_ders_ad.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Öğrenci sayısı:").grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )
    entry_ogr_sayi = ttk.Entry(form_frame, width=8)
    entry_ogr_sayi.grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(form_frame, text="Sınav süresi (dk):").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )
    entry_sure = ttk.Entry(form_frame, width=8)
    entry_sure.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Sınav türü:").grid(
        row=2, column=2, padx=5, pady=5, sticky="w"
    )
    entry_tur = ttk.Entry(form_frame, width=15)
    entry_tur.grid(row=2, column=3, padx=5, pady=5)

    sinav_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        form_frame, text="Bu dersin sınavı olacak", variable=sinav_var
    ).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def ders_ekle_click():
        hoca_id_str = entry_hoca_id.get().strip()
        ders_ad = entry_ders_ad.get().strip()
        ogr_sayi_str = entry_ogr_sayi.get().strip()
        sure_str = entry_sure.get().strip()
        sinav_turu = entry_tur.get().strip() or "yazılı"

        # Bölüm ID
        if bolum_id is not None:
            hedef_bolum_id = bolum_id
        else:
            bolum_id_str = entry_bolum_id.get().strip()
            if not bolum_id_str:
                messagebox.showwarning("Uyarı", "Bölüm ID boş olamaz.")
                return
            try:
                hedef_bolum_id = int(bolum_id_str)
            except ValueError:
                messagebox.showwarning("Uyarı", "Bölüm ID sayısal olmalı.")
                return

        if not (hoca_id_str and ders_ad and ogr_sayi_str and sure_str):
            messagebox.showwarning("Uyarı", "Tüm alanları doldur.")
            return

        try:
            hoca_id = int(hoca_id_str)
            ogr_sayi = int(ogr_sayi_str)
            sure = int(sure_str)
        except ValueError:
            messagebox.showwarning(
                "Uyarı", "Hoca ID, öğrenci sayısı ve süre sayısal olmalı."
            )
            return

        ders_ekle(
            ders_ad,
            hedef_bolum_id,
            hoca_id,
            ogr_sayi,
            sure,
            sinav_turu,
            sinav_var.get(),
        )

        # Alanları temizle
        if bolum_id is None:
            entry_bolum_id.delete(0, tk.END)
        entry_hoca_id.delete(0, tk.END)
        entry_ders_ad.delete(0, tk.END)
        entry_ogr_sayi.delete(0, tk.END)
        entry_sure.delete(0, tk.END)
        entry_tur.delete(0, tk.END)
        sinav_var.set(True)

        refresh_ders(bolum_id)
        messagebox.showinfo("Bilgi", "Ders eklendi.")

    ttk.Button(form_frame, text="Ekle", command=ders_ekle_click).grid(
        row=3, column=3, padx=5, pady=5, sticky="e"
    )

    list_frame = ttk.LabelFrame(frame, text="Dersler")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = (
        "id",
        "ders_adi",
        "fakulte",
        "bolum",
        "hoca",
        "ogr_sayi",
        "sure",
        "tur",
        "durum",
    )
    ders_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=10
    )
    for col, text, w in [
        ("id", "ID", 50),
        ("ders_adi", "Ders", 150),
        ("fakulte", "Fakülte", 130),
        ("bolum", "Bölüm", 130),
        ("hoca", "Hoca", 130),
        ("ogr_sayi", "Öğrenci", 70),
        ("sure", "Süre", 60),
        ("tur", "Tür", 80),
        ("durum", "Durum", 90),
    ]:
        ders_tree.heading(col, text=text)
        ders_tree.column(
            col,
            width=w,
            anchor="center" if col in ("id", "ogr_sayi", "sure") else "w",
        )

    ders_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=ders_tree.yview
    )
    ders_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def ders_sil_click():
        selected = ders_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir ders seç.")
            return
        item = ders_tree.item(selected[0])
        ders_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {ders_id} dersi silmek istiyor musun?"
        ):
            return
        try:
            ders_sil(ders_id)
            refresh_ders(bolum_id)
            messagebox.showinfo("Bilgi", "Ders silindi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Ders silinirken hata oluştu:\n{e}")

    btn_del = ttk.Button(frame, text="Seçili Dersi Sil", command=ders_sil_click)
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_ders(bolum_id)


# ===================== HOCA MÜSAİTLİK SEKME =====================

def refresh_musaitlik():
    global musaitlik_tree
    clear_tree(musaitlik_tree)
    for m in hoca_musaitlik_listele():
        # m: (id, hoca_ad, gun, baslangic, bitis, aciklama)
        musaitlik_tree.insert("", "end", values=m)


def create_musaitlik_tab(notebook):
    global musaitlik_tree

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Hoca Müsaitlik")

    form_frame = ttk.LabelFrame(frame, text="Müsaitlik Ekle")
    form_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(form_frame, text="Hoca ID:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_hoca_id = ttk.Entry(form_frame, width=8)
    entry_hoca_id.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Gün (örn: Salı):").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    entry_gun = ttk.Entry(form_frame, width=12)
    entry_gun.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(form_frame, text="Başlangıç (HH:MM):").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    entry_bas = ttk.Entry(form_frame, width=8)
    entry_bas.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Bitiş (HH:MM):").grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )
    entry_bit = ttk.Entry(form_frame, width=8)
    entry_bit.grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(form_frame, text="Açıklama:").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )
    entry_aciklama = ttk.Entry(form_frame, width=40)
    entry_aciklama.grid(
        row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w"
    )

    def musaitlik_ekle_click():
        hoca_id_str = entry_hoca_id.get().strip()
        gun = entry_gun.get().strip()
        bas = entry_bas.get().strip()
        bit = entry_bit.get().strip()
        aciklama = entry_aciklama.get().strip()

        if not (hoca_id_str and gun and bas and bit):
            messagebox.showwarning(
                "Uyarı", "Hoca ID, gün ve saat alanları boş olamaz."
            )
            return
        try:
            hoca_id = int(hoca_id_str)
        except ValueError:
            messagebox.showwarning("Uyarı", "Hoca ID sayısal olmalı.")
            return

        hoca_musaitlik_ekle(hoca_id, gun, bas, bit, aciklama or None)

        entry_hoca_id.delete(0, tk.END)
        entry_gun.delete(0, tk.END)
        entry_bas.delete(0, tk.END)
        entry_bit.delete(0, tk.END)
        entry_aciklama.delete(0, tk.END)

        refresh_musaitlik()
        messagebox.showinfo("Bilgi", "Müsaitlik eklendi.")

    ttk.Button(form_frame, text="Ekle", command=musaitlik_ekle_click).grid(
        row=3, column=3, padx=5, pady=5, sticky="e"
    )

    list_frame = ttk.LabelFrame(frame, text="Müsaitlikler")
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "hoca_ad", "gun", "baslangic", "bitis", "aciklama")
    musaitlik_tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", height=10
    )

    for col, text, w in [
        ("id", "ID", 50),
        ("hoca_ad", "Hoca", 150),
        ("gun", "Gün", 80),
        ("baslangic", "Başlangıç", 80),
        ("bitis", "Bitiş", 80),
        ("aciklama", "Açıklama", 250),
    ]:
        musaitlik_tree.heading(col, text=text)
        musaitlik_tree.column(
            col,
            width=w,
            anchor="center"
            if col in ("id", "gun", "baslangic", "bitis")
            else "w",
        )

    musaitlik_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=musaitlik_tree.yview
    )
    musaitlik_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def musaitlik_sil_click():
        selected = musaitlik_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silmek için bir müsaitlik seç.")
            return
        item = musaitlik_tree.item(selected[0])
        musaitlik_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {musaitlik_id} müsaitliği silmek istiyor musun?"
        ):
            return
        try:
            hoca_musaitlik_sil(musaitlik_id)
            refresh_musaitlik()
            messagebox.showinfo("Bilgi", "Müsaitlik silindi.")
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Müsaitlik silinirken hata oluştu:\n{e}"
            )

    btn_del = ttk.Button(
        frame, text="Seçili Müsaitliği Sil", command=musaitlik_sil_click
    )
    btn_del.pack(anchor="e", padx=10, pady=5)

    refresh_musaitlik()


# ===================== SINAVLAR + OTOMATİK PLANLAMA SEKME =====================

def refresh_sinav():
    global sinav_tree
    clear_tree(sinav_tree)
    for s in sinav_listele():
        (
            sinav_id,
            ders_adi,
            bolum_adi,
            fakulte_adi,
            ogretim_uyesi,
            tarih,
            saat,
            derslik_adi,
        ) = s
        sinav_tree.insert(
            "",
            "end",
            values=(
                sinav_id,
                tarih,
                saat,
                derslik_adi,
                ders_adi,
                bolum_adi,
                fakulte_adi,
                ogretim_uyesi,
            ),
        )


# ===================== SINAVLAR + OTOMATİK PLANLAMA SEKME =====================

def create_sinav_tab(notebook, user=None):
    """
    Admin      → tek tablo, tüm sınavlar (filtre + CSV çıktı)
    Bölüm yet. → iki tablo (kendi bölümü / diğer bölümler)
    Hoca       → tek tablo ama sadece kendi sınavları
    Öğrenci    → tek tablo ama sadece kendi bölümünün sınavları
    """
    global sinav_tree

    # Kullanıcı bilgileri
    rol = None
    bolum_id = None
    ogretim_uyesi_id = None

    if user:
        rol = user.get("rol")
        bolum_id = user.get("bolum_id")
        ogretim_uyesi_id = user.get("ogretim_uyesi_id")

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Sınavlar & Planlama")

    # ---------------------------------------------------------
    # 1) ADMIN ARAYÜZÜ  (TEK TABLO, TÜM SINAVLAR)
    # ---------------------------------------------------------
    if rol in (None, "admin"):
        # --- Otomatik planlama ---
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Otomatik Planlama (Admin):").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        def otomatik_planlama_click():
            try:
                atananlar = otomatik_planla()
                refresh_admin_table()

                if not atananlar:
                    messagebox.showinfo("Bilgi", "Planlanacak ders yok.")
                    return

                satirlar = []
                for a in atananlar:
                    ders_adi = a.get("ders_ad") or f"Ders ID {a.get('ders_id')}"
                    durum = a.get("durum") or ""
                    aciklama = a.get("aciklama") or ""

                    # Daha okunaklı, ders bazlı özet
                    satir = f"- {ders_adi}: {durum}"
                    if aciklama:
                        # Yeni satırla detayları ekle
                        satir += f"\n  {aciklama}"
                    satirlar.append(satir)

                mesaj = "\n\n".join(satirlar)
                messagebox.showinfo("Otomatik Planlama Sonucu", mesaj)
            except Exception as e:
                # Buraya düşerse muhtemelen veritabanı/bağlantı gibi beklenmedik bir hata vardır
                messagebox.showerror(
                    "Hata",
                    "Otomatik planlama sırasında beklenmeyen bir hata oluştu.\n"
                    f"Ayrıntı (geliştirici için):\n{e}"
                )


        ttk.Button(
            top_frame,
            text="Otomatik Planla",
            command=otomatik_planlama_click,
        ).grid(row=0, column=1, padx=10)

        # --- Fakülte / Bölüm filtreleri ---
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Fakülte listesi
        fakulte_kayitlari = fakulte_listele()  # (id, ad)
        fakulte_ad_list = ["Tümü"] + [f[1] for f in fakulte_kayitlari]

        ttk.Label(filter_frame, text="Fakülte:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        fakulte_var = tk.StringVar(value="Tümü")
        combo_fakulte = ttk.Combobox(
            filter_frame,
            textvariable=fakulte_var,
            values=fakulte_ad_list,
            state="readonly",
            width=25,
        )
        combo_fakulte.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Bölüm listesi
        bolum_kayitlari = bolum_listele()  # (id, bolum_adi, fakulte_adi)
        bolum_ad_list = ["Tümü"] + [b[1] for b in bolum_kayitlari]

        ttk.Label(filter_frame, text="Bölüm:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        bolum_var = tk.StringVar(value="Tümü")
        combo_bolum = ttk.Combobox(
            filter_frame,
            textvariable=bolum_var,
            values=bolum_ad_list,
            state="readonly",
            width=25,
        )
        combo_bolum.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # --- Manuel sınav ekle (admin için) ---
        manu = ttk.LabelFrame(frame, text="Manuel Sınav Ekle")
        manu.pack(fill="x", padx=10, pady=5)

        ttk.Label(manu, text="Ders ID:").grid(row=0, column=0, padx=5, pady=5)
        e_ders = ttk.Entry(manu, width=10)
        e_ders.grid(row=0, column=1, padx=5)

        ttk.Label(manu, text="Derslik ID:").grid(row=0, column=2, padx=5, pady=5)
        e_derslik = ttk.Entry(manu, width=10)
        e_derslik.grid(row=0, column=3, padx=5)

        ttk.Label(manu, text="Tarih (YYYY-MM-DD):").grid(
            row=1, column=0, padx=5, pady=5
        )
        e_tarih = ttk.Entry(manu, width=12)
        e_tarih.grid(row=1, column=1)

        ttk.Label(manu, text="Saat (HH:MM):").grid(
            row=1, column=2, padx=5, pady=5
        )
        e_saat = ttk.Entry(manu, width=10)
        e_saat.grid(row=1, column=3)

        def manuel_ekle():
            try:
                sinav_ekle(
                    int(e_ders.get()),
                    e_tarih.get().strip(),
                    e_saat.get().strip(),
                    int(e_derslik.get()),
                )
                messagebox.showinfo("Başarılı", "Sınav eklendi.")
                e_ders.delete(0, tk.END)
                e_derslik.delete(0, tk.END)
                e_tarih.delete(0, tk.END)
                e_saat.delete(0, tk.END)
                refresh_admin_table()
            except Exception as e:
                msg = str(e)
                if "uniq_derslik_zaman" in msg or "Duplicate entry" in msg:
                    turkce = (
                        "Bu tarih ve saatte bu derslikte zaten bir sınav var.\n"
                        "Lütfen farklı bir saat veya derslik seç."
                    )
                else:
                    turkce = "Beklenmeyen bir hata oluştu:\n" + msg

                messagebox.showerror("Hata", turkce)


        ttk.Button(manu, text="Ekle", command=manuel_ekle).grid(
            row=0, column=4, rowspan=2, padx=10
        )

        # --- TEK TABLO: TÜM SINAVLAR ---
        lbl = ttk.Label(
            frame,
            text="Tüm Sınavlar",
            font=("Segoe UI", 10, "bold"),
        )
        lbl.pack(anchor="w", padx=10, pady=(10, 0))

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", padx=10, pady=5, expand=True)

        cols = ("id", "tarih", "saat", "derslik", "ders", "bolum", "fakulte", "hoca")
        all_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        for col, text, w in [
            ("id", "ID", 50),
            ("tarih", "Tarih", 90),
            ("saat", "Saat", 70),
            ("derslik", "Derslik", 120),
            ("ders", "Ders", 150),
            ("bolum", "Bölüm", 130),
            ("fakulte", "Fakülte", 130),
            ("hoca", "Hoca", 150),
        ]:
            all_tree.heading(col, text=text)
            all_tree.column(
                col,
                width=w,
                anchor="center" if col in ("id", "tarih", "saat") else "w",
            )

        all_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=all_tree.yview
        )
        all_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # dışarıdan erişmek istersen diye
        sinav_tree = all_tree

        def refresh_admin_table():
            # tabloyu temizle
            for t in all_tree.get_children():
                all_tree.delete(t)

            secilen_fakulte = fakulte_var.get()
            secilen_bolum = bolum_var.get()

            exams = sinav_listele()  # Tüm sınavlar dict şeklinde

            for s in exams:
                # Fakülte filtresi
                if secilen_fakulte and secilen_fakulte != "Tümü":
                    if s["fakulte_ad"] != secilen_fakulte:
                        continue

                # Bölüm filtresi
                if secilen_bolum and secilen_bolum != "Tümü":
                    if s["bolum_ad"] != secilen_bolum:
                        continue

                all_tree.insert(
                    "",
                    "end",
                    values=(
                        s["id"],
                        s["tarih"],
                        s["saat"],
                        s["derslik_ad"],
                        s["ders_ad"],
                        s["bolum_ad"],
                        s["fakulte_ad"],
                        s["hoca_ad"],
                    ),
                )

        def on_filter_change(event=None):
            refresh_admin_table()

        combo_fakulte.bind("<<ComboboxSelected>>", on_filter_change)
        combo_bolum.bind("<<ComboboxSelected>>", on_filter_change)

        def export_to_csv():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV dosyası", "*.csv"), ("Tüm dosyalar", "*.*")]
            )
            if not file_path:
                return

            secilen_fakulte = fakulte_var.get()
            secilen_bolum = bolum_var.get()

            exams = sinav_listele()  # Tüm sınavlar

            try:
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["ID", "Tarih", "Saat", "Derslik", "Ders", "Bölüm", "Fakülte", "Hoca"]
                    )

                    for s in exams:
                        if secilen_fakulte and secilen_fakulte != "Tümü":
                            if s["fakulte_ad"] != secilen_fakulte:
                                continue
                        if secilen_bolum and secilen_bolum != "Tümü":
                            if s["bolum_ad"] != secilen_bolum:
                                continue

                        writer.writerow(
                            [
                                s["id"],
                                s["tarih"],
                                s["saat"],
                                s["derslik_ad"],
                                s["ders_ad"],
                                s["bolum_ad"],
                                s["fakulte_ad"],
                                s["hoca_ad"],
                            ]
                        )

                messagebox.showinfo(
                    "Bilgi", f"Sınav programı CSV olarak kaydedildi:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Hata", f"Dışa aktarım sırasında hata:\n{e}")

        def delete_exam():
            sel = all_tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Uyarı", "Silmek için bir sınav seçmelisin."
                )
                return

            sinav_id = all_tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Onay", f"ID {sinav_id} sınavı silinsin mi?"):
                sinav_sil(sinav_id)
                refresh_admin_table()

        ttk.Button(
            frame,
            text="Sınav Programını CSV Olarak Dışa Aktar",
            command=export_to_csv,
        ).pack(anchor="w", padx=10, pady=5)

        ttk.Button(frame, text="Seçili Sınavı Sil", command=delete_exam).pack(
            anchor="e", padx=10, pady=10
        )

        # ilk yükleme
        refresh_admin_table()
        return  # Admin için aşağıdaki yapı kullanılmayacak

    # ---------------------------------------------------------
    # 2) ADMIN OLMAYANLAR  (BÖLÜM YET., HOCA, ÖĞRENCİ)
    #    – ESKİ İKİ TABLO YAPISI
    # ---------------------------------------------------------

    # Bölüm yetkilisi için manuel ekleme (hoca / öğrenci göremez)
    if rol == "bolum_yetkilisi":
        manu = ttk.LabelFrame(frame, text="Manuel Sınav Ekle")
        manu.pack(fill="x", padx=10, pady=5)

        ttk.Label(manu, text="Ders ID:").grid(row=0, column=0, padx=5, pady=5)
        e_ders = ttk.Entry(manu, width=10)
        e_ders.grid(row=0, column=1, padx=5)

        ttk.Label(manu, text="Derslik ID:").grid(row=0, column=2, padx=5, pady=5)
        e_derslik = ttk.Entry(manu, width=10)
        e_derslik.grid(row=0, column=3, padx=5)

        ttk.Label(manu, text="Tarih (YYYY-MM-DD):").grid(
            row=1, column=0, padx=5, pady=5
        )
        e_tarih = ttk.Entry(manu, width=12)
        e_tarih.grid(row=1, column=1)

        ttk.Label(manu, text="Saat (HH:MM):").grid(
            row=1, column=2, padx=5, pady=5
        )
        e_saat = ttk.Entry(manu, width=10)
        e_saat.grid(row=1, column=3)

        def manuel_ekle_bolum():
            try:
                sinav_ekle(
                    int(e_ders.get()),
                    e_tarih.get().strip(),
                    e_saat.get().strip(),
                    int(e_derslik.get()),
                )
                messagebox.showinfo("Başarılı", "Sınav eklendi.")
                e_ders.delete(0, tk.END)
                e_derslik.delete(0, tk.END)
                e_tarih.delete(0, tk.END)
                e_saat.delete(0, tk.END)
                refresh_tables()
            except Exception as e:
                msg = str(e)
                if "uniq_derslik_zaman" in msg or "Duplicate entry" in msg:
                    turkce = (
                        "Bu tarih ve saatte bu derslikte zaten bir sınav var.\n"
                        "Lütfen farklı bir saat veya derslik seç."
                    )
                else:
                    turkce = "Beklenmeyen bir hata oluştu:\n" + msg

                messagebox.showerror("Hata", turkce)


    # --- TABLO 1: KENDİ BÖLÜMÜNÜN / KENDİSINİN SINAVLARI ---
    lbl1 = ttk.Label(
        frame,
        text="Kendi Bölümünün Sınavları",
        font=("Segoe UI", 10, "bold"),
    )
    lbl1.pack(anchor="w", padx=10)

    own_frame = ttk.Frame(frame)
    own_frame.pack(fill="both", padx=10, pady=5, expand=True)

    cols = ("id", "tarih", "saat", "derslik", "ders", "bolum", "fakulte", "hoca")
    own_tree = ttk.Treeview(own_frame, columns=cols, show="headings", height=8)
    for c in cols:
        own_tree.heading(c, text=c.capitalize())
    own_tree.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(own_frame, orient="vertical", command=own_tree.yview).pack(
        side="right", fill="y"
    )

    # --- TABLO 2: DİĞER BÖLÜMLERİN SINAVLARI (sadece bölüm yetkilisine göstermek mantıklı) ---
    lbl2 = ttk.Label(
        frame,
        text="Diğer Bölümlerin Sınavları",
        font=("Segoe UI", 10, "bold"),
    )
    lbl2.pack(anchor="w", padx=10, pady=(15, 0))

    other_frame = ttk.Frame(frame)
    other_frame.pack(fill="both", padx=10, pady=5, expand=True)

    other_tree = ttk.Treeview(other_frame, columns=cols, show="headings", height=8)
    for c in cols:
        other_tree.heading(c, text=c.capitalize())
    other_tree.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(
        other_frame, orient="vertical", command=other_tree.yview
    ).pack(side="right", fill="y")

    # sinav_tree'yi en azından own_tree'ye eşitleyelim
    sinav_tree = own_tree

    # --- Tablo doldurma fonksiyonu ---
    def refresh_tables():
        # önce temizle
        for t in own_tree.get_children():
            own_tree.delete(t)
        for t in other_tree.get_children():
            other_tree.delete(t)

        # kendi bölümünün / hocanın sınavları
        exams_own = sinav_listele(
            bolum_id=bolum_id,
            ogretim_uyesi_id=ogretim_uyesi_id,
        )
        for s in exams_own:
            own_tree.insert(
                "",
                "end",
                values=(
                    s["id"],
                    s["tarih"],
                    s["saat"],
                    s["derslik_ad"],
                    s["ders_ad"],
                    s["bolum_ad"],
                    s["fakulte_ad"],
                    s["hoca_ad"],
                ),
            )

        # diğer bölümlerin sınavları – sadece bölüm id varsa mantıklı
        if bolum_id is not None:
            other_exams = sinav_listele(bolum_id=bolum_id, diger_bolumler=True)
            for s in other_exams:
                other_tree.insert(
                    "",
                    "end",
                    values=(
                        s["id"],
                        s["tarih"],
                        s["saat"],
                        s["derslik_ad"],
                        s["ders_ad"],
                        s["bolum_ad"],
                        s["fakulte_ad"],
                        s["hoca_ad"],
                    ),
                )

    # --- Sınav silme (sadece bölüm yetkilisi) ---
    if rol == "bolum_yetkilisi":
        def delete_exam():
            sel = own_tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Uyarı", "Sadece kendi bölümüne ait sınav silinebilir."
                )
                return

            sinav_id = own_tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Onay", f"ID {sinav_id} sınavı silinsin mi?"):
                sinav_sil(sinav_id)
                refresh_tables()

        ttk.Button(
            frame, text="Seçili Sınavı Sil", command=delete_exam
        ).pack(anchor="e", padx=10, pady=10)

    # İlk yükleme
    refresh_tables()





# ===================== KULLANICI YÖNETİMİ SEKME (SADECE ADMIN) =====================

def create_kullanici_tab(notebook):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Kullanıcı Yönetimi")

    # Verileri çekmek için map hazırlıkları
    bolum_kayitlari = bolum_listele()  # (id, bolum_adi, fakulte_adi)
    bolum_display_to_id = {}
    bolum_display_list = []
    for b_id, b_ad, f_ad in bolum_kayitlari:
        s = f"{b_id} - {b_ad} ({f_ad})"
        bolum_display_to_id[s] = b_id
        bolum_display_list.append(s)

    hoca_kayitlari = ogretim_uyesi_listele()  # (id, ad_soyad, bolum_adi)
    hoca_display_to_id = {}
    hoca_display_list = []
    for h_id, ad_soyad, bolum_adi in hoca_kayitlari:
        s = f"{h_id} - {ad_soyad} ({bolum_adi})"
        hoca_display_to_id[s] = h_id
        hoca_display_list.append(s)

    # ==== ÜST FORM ====
    form = ttk.LabelFrame(frame, text="Yeni Kullanıcı Ekle")
    form.pack(fill="x", padx=10, pady=5)

    ttk.Label(form, text="Kullanıcı Adı (mail):").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    entry_mail = ttk.Entry(form, width=40)
    entry_mail.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form, text="Şifre (TCKN):").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    entry_sifre = ttk.Entry(form, width=40)
    entry_sifre.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form, text="Rol:").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )
    rol_var = tk.StringVar()
    combo_rol = ttk.Combobox(
        form,
        textvariable=rol_var,
        state="readonly",
        values=["admin", "bolum_yetkilisi", "hoca", "ogrenci"],
    )
    combo_rol.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(form, text="Bölüm (Öğrenci / Bölüm Yet.):").grid(
        row=3, column=0, padx=5, pady=5, sticky="w"
    )
    bolum_var = tk.StringVar()
    combo_bolum = ttk.Combobox(
        form,
        textvariable=bolum_var,
        state="readonly",
        values=bolum_display_list,
        width=40,
    )
    combo_bolum.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(form, text="Hoca (Hoca kullanıcıları için):").grid(
        row=4, column=0, padx=5, pady=5, sticky="w"
    )
    hoca_var = tk.StringVar()
    combo_hoca = ttk.Combobox(
        form,
        textvariable=hoca_var,
        state="readonly",
        values=hoca_display_list,
        width=40,
    )
    combo_hoca.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    def rol_degisti(event=None):
        rol = rol_var.get()
        if rol == "ogrenci":
            combo_bolum.configure(state="readonly")
            combo_hoca.configure(state="disabled")
        elif rol == "bolum_yetkilisi":
            combo_bolum.configure(state="readonly")
            combo_hoca.configure(state="disabled")
        elif rol == "hoca":
            combo_bolum.configure(state="disabled")
            combo_hoca.configure(state="readonly")
        elif rol == "admin":
            combo_bolum.configure(state="disabled")
            combo_hoca.configure(state="disabled")

    combo_rol.bind("<<ComboboxSelected>>", rol_degisti)

    # ==== KULLANICI TABLOSU ====

    table_frame = ttk.LabelFrame(frame, text="Kullanıcılar")
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(
        table_frame,
        columns=("id", "mail", "rol", "bolum_id", "hoca_id"),
        show="headings",
        height=10,
    )
    tree.heading("id", text="ID")
    tree.heading("mail", text="Kullanıcı Adı")
    tree.heading("rol", text="Rol")
    tree.heading("bolum_id", text="Bölüm ID")
    tree.heading("hoca_id", text="Hoca ID")

    tree.column("id", width=40, anchor="center")
    tree.column("rol", width=100, anchor="center")
    tree.column("bolum_id", width=80, anchor="center")
    tree.column("hoca_id", width=80, anchor="center")
    tree.column("mail", width=240, anchor="w")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        table_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def tablo_yenile():
        for i in tree.get_children():
            tree.delete(i)
        for k in kullanici_listele():
            tree.insert(
                "",
                "end",
                values=(
                    k["id"],
                    k["kullanici_adi"],
                    k["rol"],
                    k["bolum_id"],
                    k["ogretim_uyesi_id"],
                ),
            )

    tablo_yenile()

    def ekle_click():
        mail = entry_mail.get().strip()
        sifre = entry_sifre.get().strip()
        rol = rol_var.get().strip()

        if not mail or not sifre or not rol:
            messagebox.showwarning(
                "Uyarı", "Mail, şifre ve rol boş bırakılamaz."
            )
            return

        bolum_id = None
        ogretim_uyesi_id = None

        if rol == "ogrenci" or rol == "bolum_yetkilisi":
            bolum_disp = bolum_var.get().strip()
            if not bolum_disp:
                messagebox.showwarning(
                    "Uyarı", "Bu rol için bölüm seçmelisin."
                )
                return
            bolum_id = bolum_display_to_id.get(bolum_disp)
        elif rol == "hoca":
            hoca_disp = hoca_var.get().strip()
            if not hoca_disp:
                messagebox.showwarning(
                    "Uyarı", "Hoca kullanıcısı için hoca seçmelisin."
                )
                return
            ogretim_uyesi_id = hoca_display_to_id.get(hoca_disp)

        try:
            kullanici_ekle(mail, sifre, rol, bolum_id, ogretim_uyesi_id)
            messagebox.showinfo("Bilgi", "Kullanıcı eklendi.")
            entry_mail.delete(0, tk.END)
            entry_sifre.delete(0, tk.END)
            bolum_var.set("")
            hoca_var.set("")
            rol_var.set("")
            tablo_yenile()
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Kullanıcı eklenirken hata oluştu:\n{e}"
            )

    ttk.Button(form, text="Kullanıcı Ekle", command=ekle_click).grid(
        row=5, column=1, padx=5, pady=10, sticky="e"
    )

    def sil_click():
        secim = tree.selection()
        if not secim:
            messagebox.showwarning(
                "Uyarı", "Silmek için bir kullanıcı seçmelisin."
            )
            return
        item = tree.item(secim[0])
        k_id = item["values"][0]
        if not messagebox.askyesno(
            "Onay", f"ID {k_id} kullanıcısını silmek istiyor musun?"
        ):
            return
        try:
            kullanici_sil(k_id)
            messagebox.showinfo("Bilgi", "Kullanıcı silindi.")
            tablo_yenile()
        except Exception as e:
            messagebox.showerror(
                "Hata", f"Kullanıcı silinirken hata oluştu:\n{e}"
            )

    ttk.Button(
        frame, text="Seçili Kullanıcıyı Sil", command=sil_click
    ).pack(anchor="e", padx=10, pady=5)


# ===================== ANA PENCERE / ROL BAZLI BUILDER'LAR =====================

def build_admin_gui(user=None):
    root = tk.Tk()
    apply_theme(root)
    root.title("Üniversite Sınav Planlama Sistemi - Admin")
    root.geometry("1100x700")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    create_fakulte_tab(notebook)
    create_bolum_tab(notebook)
    create_ogretim_tab(notebook)
    create_derslik_tab(notebook)
    create_ders_tab(notebook)
    create_musaitlik_tab(notebook)
    create_kullanici_tab(notebook)
    create_sinav_tab(notebook, user)

    root.mainloop()


def build_bolum_yetkilisi_gui(user):
    """
    Bölüm yetkilisi: kendi bölümüne ait
      - öğretim üyelerini
      - dersleri
      - sınav programını
    yönetir/görür.
    """
    root = tk.Tk()
    root.title("Üniversite Sınav Sistemi - Bölüm Yetkilisi")
    root.geometry("1000x650")
    apply_theme(root)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    bolum_id = user.get("bolum_id")

    # Kendi bölümünün hocaları + dersleri
    create_ogretim_tab(notebook, bolum_id=bolum_id)
    create_ders_tab(notebook, bolum_id=bolum_id)

    # Müsaitlik ve sınavlar (sınav tablosu zaten bolum_id ile filtreliyor)
    create_musaitlik_tab(notebook)
    create_sinav_tab(notebook, user)

    root.mainloop()



def build_hoca_gui(user):
    """
    Hoca: Sadece kendi sınav programını görür.
    Şu an create_sinav_tab tüm sınavları listeliyor; ileride sinav_listele
    fonksiyonunu ogretim_uyesi_id parametresiyle genişletip filtreleyebilirsin.
    """
    root = tk.Tk()
    apply_theme(root)
    root.title("Üniversite Sınav Sistemi - Hoca")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    create_sinav_tab(notebook, user)

    root.mainloop()


def build_ogrenci_gui(user):
    """
    Öğrenci: Sadece kendi bölümünün sınav programını görür.
    Şimdilik tüm sınavlar görünüyor; sinav_listele tarafında bolum_id filtresi
    ekleyerek bunu daraltabilirsin.
    """
    root = tk.Tk()
    apply_theme(root)
    root.title("Üniversite Sınav Sistemi - Öğrenci")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    create_sinav_tab(notebook, user)

    root.mainloop()


def main():
    # Eskiden doğrudan admin paneli CLI yerine GUI açıyordun.
    # Şimdi login ekranından da çağırılabilir, ama buradan direkt test için
    # admin GUI'sini açmak istersen diye bıraktım.
    build_admin_gui(user=None)


if __name__ == "__main__":
    main()
