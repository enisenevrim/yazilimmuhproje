import tkinter as tk
from ui.arayuz import BudgetTrackerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTrackerApp(root)
    root.mainloop()
    import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker - Kişisel Bütçe ve Harcama Takip")
        self.root.geometry("950x650")
        self.root.configure(bg="#f4f6f9")

        # Geçici test verisi (Beyza'nın veri_yonetimi.py modülü bağlanınca oradan gelecek)
        self.aktif_kullanici = None
        self.ornek_veriler = {
            "enise@mail.com": {
                "kullanici_adi": "Enise Havva",
                "sifre": "1234",
                "islemler": [
                    {"id": 1, "tur": "gelir", "tutar": 5000.00, "kategori": "Burs/Maaş", "tarih": "2026-11-01", "aciklama": "KYK Bursu"},
                    {"id": 2, "tur": "gider", "tutar": 850.00, "kategori": "Market", "tarih": "2026-11-10", "aciklama": "Haftalık mutfak"},
                    {"id": 3, "tur": "gider", "tutar": 820.00, "kategori": "Eğlence", "tarih": "2026-11-15", "aciklama": "Sinema ve kafe"}
                ],
                "limitler": {
                    "Market": 1500.00,
                    "Ulaşım": 600.00,
                    "Fatura": 1000.00,
                    "Eğlence": 1000.00,
                    "Eğitim": 800.00
                },
                "hedefler": [
                    {"id": 1, "hedef_adi": "Yeni Laptop", "hedef_tutar": 25000.00, "biriken_tutar": 7500.00, "tamamlandi": False}
                ],
                "rozetler": ["Düzenli Kayıtçı"]
            }
        }

        self.giris_ekrani_olustur()

    def ekrani_temizle(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. KULLANICI GİRİŞ VE KAYIT EKRANI
    # ==========================================
    def giris_ekrani_olustur(self):
        self.ekrani_temizle()
        cerceve = tk.Frame(self.root, bg="white", padx=40, pady=40, relief="groove", bd=1)
        cerceve.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(cerceve, text="Budget Tracker", font=("Segoe UI", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=(0, 5))
        tk.Label(cerceve, text="Kişisel Bütçe ve Harcama Takip Sistemi", font=("Segoe UI", 10), bg="white", fg="#7f8c8d").pack(pady=(0, 20))

        tk.Label(cerceve, text="Kullanıcı Adı (Sadece Kayıt İçin):", bg="white", anchor="w").pack(fill="x")
        self.ent_ad = ttk.Entry(cerceve, width=35)
        self.ent_ad.pack(pady=(2, 10))

        tk.Label(cerceve, text="E-posta:", bg="white", anchor="w").pack(fill="x")
        self.ent_email = ttk.Entry(cerceve, width=35)
        self.ent_email.insert(0, "enise@mail.com")
        self.ent_email.pack(pady=(2, 10))

        tk.Label(cerceve, text="Şifre:", bg="white", anchor="w").pack(fill="x")
        self.ent_sifre = ttk.Entry(cerceve, width=35, show="*")
        self.ent_sifre.insert(0, "1234")
        self.ent_sifre.pack(pady=(2, 20))

        btn_frame = tk.Frame(cerceve, bg="white")
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Giriş Yap", bg="#2980b9", fg="white", font=("Segoe UI", 10, "bold"), width=14, command=self.giris_yap_tiklandi).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Kayıt Ol", bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), width=14, command=self.kayit_ol_tiklandi).pack(side="right", padx=5)

    def giris_yap_tiklandi(self):
        email = self.ent_email.get().strip()
        sifre = self.ent_sifre.get().strip()

        if email in self.ornek_veriler and self.ornek_veriler[email]["sifre"] == sifre:
            self.aktif_kullanici = email
            self.ana_ekran_olustur()
        else:
            messagebox.showerror("Giriş Hatası", "Hatalı e-posta veya şifre girdiniz!")

    def kayit_ol_tiklandi(self):
        ad = self.ent_ad.get().strip()
        email = self.ent_email.get().strip()
        sifre = self.ent_sifre.get().strip()

        if not ad or not email or not sifre:
            messagebox.showwarning("Eksik Bilgi", "Kayıt için tüm alanları doldurmalısınız.")
            return
        if email in self.ornek_veriler:
            messagebox.showerror("Kayıt Hatası", "Bu e-posta adresi ile zaten kayıt olunmuş!")
            return

        self.ornek_veriler[email] = {
            "kullanici_adi": ad,
            "sifre": sifre,
            "islemler": [],
            "limitler": {"Market": 1000.0, "Ulaşım": 500.0, "Fatura": 1000.0, "Eğlence": 500.0, "Eğitim": 500.0},
            "hedefler": [],
            "rozetler": []
        }
        messagebox.showinfo("Başarılı", "Kayıt tamamlandı! Şimdi giriş yapabilirsiniz.")

    # ==========================================
    # 2. ANA KONTROL PANELİ (DASHBOARD)
    # ==========================================
    def ana_ekran_olustur(self):
        self.ekrani_temizle()
        veri = self.ornek_veriler[self.aktif_kullanici]

        # Üst Bilgi Çubuğu (Kullanıcı Adı, Güncel Bakiye ve Çıkış)
        ust_bar = tk.Frame(self.root, bg="#2c3e50", height=60, padx=20)
        ust_bar.pack(fill="x")

        tk.Label(ust_bar, text=f"Hoş Geldin, {veri['kullanici_adi']}", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white").pack(side="left", pady=15)

        self.lbl_bakiye = tk.Label(ust_bar, text="Güncel Bakiye: 0.00 TL", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="#2ecc71")
        self.lbl_bakiye.pack(side="left", padx=40)

        tk.Button(ust_bar, text="Çıkış Yap", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=self.giris_ekrani_olustur).pack(side="right", pady=15)

        # Uyarı Bildirim Alanı (%80 Sarı / %100 Kırmızı Uyarılar İçin)
        self.uyari_alani = tk.Frame(self.root, bg="#f4f6f9", padx=20, pady=5)
        self.uyari_alani.pack(fill="x")

        # Sekmeli Yapı (İşlemler | Bütçe Limitleri & Rapor | Tasarruf & Rozetler)
        sekmeler = ttk.Notebook(self.root)
        sekmeler.pack(fill="both", expand=True, padx=20, pady=10)

        self.sekme_islemler = tk.Frame(sekmeler, bg="white", padx=15, pady=15)
        self.sekme_butce = tk.Frame(sekmeler, bg="white", padx=15, pady=15)
        self.sekme_hedefler = tk.Frame(sekmeler, bg="white", padx=15, pady=15)

        sekmeler.add(self.sekme_islemler, text="  Gelir / Gider İşlemleri  ")
        sekmeler.add(self.sekme_butce, text="  Bütçe Limitleri & Özet  ")
        sekmeler.add(self.sekme_hedefler, text="  Tasarruf Hedefleri & Rozetler  ")

        self.islemler_sekmesini_doldur()
        self.butce_sekmesini_doldur()
        self.hedefler_sekmesini_doldur()
        self.ekrani_guncelle()

    # ==========================================
    # SEKME 1: İŞLEM EKLEME, SİLME VE LİSTELEME
    # ==========================================
    def islemler_sekmesini_doldur(self):
        form = tk.LabelFrame(self.sekme_islemler, text="Yeni İşlem Ekle", bg="white", padx=10, pady=10)
        form.pack(fill="x", pady=(0, 15))

        tk.Label(form, text="Tür:", bg="white").grid(row=0, column=0, padx=5)
        self.cmb_tur = ttk.Combobox(form, values=["gider", "gelir"], width=10, state="readonly")
        self.cmb_tur.set("gider")
        self.cmb_tur.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Tutar (TL):", bg="white").grid(row=0, column=2, padx=5)
        self.ent_tutar = ttk.Entry(form, width=12)
        self.ent_tutar.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Kategori:", bg="white").grid(row=0, column=4, padx=5)
        self.cmb_kategori = ttk.Combobox(form, values=["Market", "Ulaşım", "Fatura", "Eğlence", "Eğitim", "Burs/Maaş"], width=14, state="readonly")
        self.cmb_kategori.set("Market")
        self.cmb_kategori.grid(row=0, column=5, padx=5)

        tk.Label(form, text="Açıklama:", bg="white").grid(row=0, column=6, padx=5)
        self.ent_aciklama = ttk.Entry(form, width=22)
        self.ent_aciklama.grid(row=0, column=7, padx=5)

        tk.Button(form, text="+ Ekle", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=10, command=self.islem_ekle).grid(row=0, column=8, padx=10)

        # İşlem Tablosu
        kolonlar = ("id", "tarih", "tur", "kategori", "tutar", "aciklama")
        self.tablo = ttk.Treeview(self.sekme_islemler, columns=kolonlar, show="headings", height=12)
        for kol, baslik in zip(kolonlar, ["ID", "Tarih", "Tür", "Kategori", "Tutar (TL)", "Açıklama"]):
            self.tablo.heading(kol, text=baslik)
            self.tablo.column(kol, width=110 if kol != "aciklama" else 220, anchor="center")
        self.tablo.pack(fill="both", expand=True)

        self.lbl_bos_liste = tk.Label(self.sekme_islemler, text="", bg="white", fg="#7f8c8d", font=("Segoe UI", 10, "italic"))
        self.lbl_bos_liste.pack(pady=5)

        tk.Button(self.sekme_islemler, text="Seçili İşlemi Sil", bg="#c0392b", fg="white", command=self.islem_sil).pack(anchor="e", pady=5)

    def islem_ekle(self):
        try:
            tutar = round(float(self.ent_tutar.get().replace(",", ".")), 2)
            if tutar <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Geçersiz Tutar", "Tutar sıfırdan büyük sayısal bir değer olmalıdır!")
            return

        veri = self.ornek_veriler[self.aktif_kullanici]
        yeni_id = len(veri["islemler"]) + 1
        yeni_islem = {
            "id": yeni_id,
            "tur": self.cmb_tur.get(),
            "tutar": tutar,
            "kategori": self.cmb_kategori.get(),
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "aciklama": self.ent_aciklama.get().strip() or "-"
        }
        veri["islemler"].append(yeni_islem)
        self.ent_tutar.delete(0, tk.END)
        self.ent_aciklama.delete(0, tk.END)
        self.ekrani_guncelle()

    def islem_sil(self):
        secili = self.tablo.selection()
        if not secili:
            messagebox.showwarning("Seçim Yok", "Silmek için tablodan bir işlem seçin.")
            return
        islem_id = self.tablo.item(secili[0])["values"][0]
        veri = self.ornek_veriler[self.aktif_kullanici]
        veri["islemler"] = [i for i in veri["islemler"] if i["id"] != islem_id]
        self.ekrani_guncelle()

    # ==========================================
    # SEKME 2: BÜTÇE LİMİTLERİ VE AYLIK ÖZET
    # ==========================================
    def butce_sekmesini_doldur(self):
        sol = tk.LabelFrame(self.sekme_butce, text="Kategori Limiti Belirle", bg="white", padx=15, pady=15)
        sol.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(sol, text="Kategori:", bg="white").pack(anchor="w")
        self.cmb_limit_kat = ttk.Combobox(sol, values=["Market", "Ulaşım", "Fatura", "Eğlence", "Eğitim"], state="readonly")
        self.cmb_limit_kat.set("Market")
        self.cmb_limit_kat.pack(fill="x", pady=(2, 10))

        tk.Label(sol, text="Aylık Limit (TL):", bg="white").pack(anchor="w")
        self.ent_limit_tutar = ttk.Entry(sol)
        self.ent_limit_tutar.pack(fill="x", pady=(2, 10))

        tk.Button(sol, text="Limiti Güncelle", bg="#2980b9", fg="white", command=self.limit_guncelle).pack(fill="x")

        self.lbl_limit_listesi = tk.Label(sol, text="", bg="white", justify="left", font=("Segoe UI", 10))
        self.lbl_limit_listesi.pack(anchor="w", pady=15)

        sag = tk.LabelFrame(self.sekme_butce, text="Aylık Özet ve Kategori Dağılımı", bg="white", padx=15, pady=15)
        sag.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_aylik_ozet = tk.Label(sag, text="", bg="white", justify="left", font=("Segoe UI", 11))
        self.lbl_aylik_ozet.pack(anchor="w")

    def limit_guncelle(self):
        try:
            yeni_limit = round(float(self.ent_limit_tutar.get().replace(",", ".")), 2)
            if yeni_limit <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Limit tutarı pozitif bir sayı olmalıdır.")
            return
        kat = self.cmb_limit_kat.get()
        self.ornek_veriler[self.aktif_kullanici]["limitler"][kat] = yeni_limit
        self.ent_limit_tutar.delete(0, tk.END)
        self.ekrani_guncelle()

    # ==========================================
    # SEKME 3: TASARRUF HEDEFLERİ VE ROZETLER
    # ==========================================
    def hedefler_sekmesini_doldur(self):
        ust = tk.LabelFrame(self.sekme_hedefler, text="Tasarruf Hedeflerim", bg="white", padx=15, pady=15)
        ust.pack(fill="x", pady=(0, 15))

        self.hedef_cercevesi = tk.Frame(ust, bg="white")
        self.hedef_cercevesi.pack(fill="x")

        alt = tk.LabelFrame(self.sekme_hedefler, text="Kazanılan Rozetlerim", bg="white", padx=15, pady=15)
        alt.pack(fill="both", expand=True)

        self.lbl_rozetler = tk.Label(alt, text="", bg="white", font=("Segoe UI", 11, "bold"), fg="#8e44ad", justify="left")
        self.lbl_rozetler.pack(anchor="w")

    # ==========================================
    # TÜM EKRAN VERİLERİNİ VE UYARILARI GÜNCELLEME
    # ==========================================
    def ekrani_guncelle(self):
        veri = self.ornek_veriler[self.aktif_kullanici]

        # Tabloyu Yenile
        for satir in self.tablo.get_children():
            self.tablo.delete(satir)

        if not veri["islemler"]:
            self.lbl_bos_liste.config(text="Henüz kayıtlı işleminiz yok.")
        else:
            self.lbl_bos_liste.config(text="")
            for i in veri["islemler"]:
                self.tablo.insert("", tk.END, values=(i["id"], i["tarih"], i["tur"].upper(), i["kategori"], f"{i['tutar']:.2f}", i["aciklama"]))

        # Bakiye ve Aylık Özet Hesabı
        toplam_gelir = sum(i["tutar"] for i in veri["islemler"] if i["tur"] == "gelir")
        toplam_gider = sum(i["tutar"] for i in veri["islemler"] if i["tur"] == "gider")
        kalan = toplam_gelir - toplam_gider

        self.lbl_bakiye.config(text=f"Güncel Bakiye: {kalan:.2f} TL")
        self.lbl_aylik_ozet.config(
            text=f"Toplam Gelir: {toplam_gelir:.2f} TL\n"
                 f"Toplam Gider: {toplam_gider:.2f} TL\n"
                 f"Kalan Bakiye: {kalan:.2f} TL"
        )

        # Limit Kontrolleri (%80 Sarı / %100 Kırmızı Uyarı)
        for w in self.uyari_alani.winfo_children():
            w.destroy()

        limit_metni = "Tanımlı Limitler:\n"
        for kat, lim in veri["limitler"].items():
            harcanan = sum(i["tutar"] for i in veri["islemler"] if i["tur"] == "gider" and i["kategori"] == kat)
            limit_metni += f"• {kat}: {harcanan:.2f} / {lim:.2f} TL\n"

            if harcanan > lim:
                asim = harcanan - lim
                tk.Label(self.uyari_alani, text=f"KIRMIZI UYARI: {kat} kategorisi limiti {asim:.2f} TL aşıldı!", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(fill="x", pady=2)
            elif harcanan >= lim * 0.80:
                tk.Label(self.uyari_alani, text=f"SARI UYARI: {kat} kategorisi harcamanız limitin %80'ine ulaştı ({harcanan:.2f}/{lim:.2f} TL).", bg="#f1c40f", fg="black", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(fill="x", pady=2)

        self.lbl_limit_listesi.config(text=limit_metni)

        # Tasarruf Hedefleri İlerleme Çubuğu
        for w in self.hedef_cercevesi.winfo_children():
            w.destroy()

        for h in veri["hedefler"]:
            oran = min(100, (h["biriken_tutar"] / h["hedef_tutar"]) * 100)
            tk.Label(self.hedef_cercevesi, text=f"{h['hedef_adi']} - {h['biriken_tutar']:.2f} / {h['hedef_tutar']:.2f} TL (%{oran:.1f})", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            bar = ttk.Progressbar(self.hedef_cercevesi, length=400, mode="determinate", value=oran)
            bar.pack(anchor="w", pady=(2, 10))

        # Rozetler
        rozet_metni = "\n".join([f"🏆 {r}" for r in veri["rozetler"]]) if veri["rozetler"] else "Henüz kazanılmış rozet yok."
        self.lbl_rozetler.config(text=rozet_metni)
    