import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Beyza ve Nezo'nun modülleri projeye eklendiğinde otomatik devreye girer
try:
    from models import veri_yonetimi as vm
    VERI_MODULU_AKTIF = True
except (ImportError, AttributeError):
    VERI_MODULU_AKTIF = False

try:
    from logic import butce_hesaplama as bh
    MANTIK_MODULU_AKTIF = True
except (ImportError, AttributeError):
    MANTIK_MODULU_AKTIF = False

# Ekranda görünen Türkçe isimler ile JSON'daki standart anahtarların eşleşmesi
KATEGORI_GORUNUM_TO_KOD = {
    "Market": "market",
    "Ulaşım": "ulasim",
    "Fatura": "fatura",
    "Eğlence": "eglence",
    "Eğitim": "egitim",
    "Burs / Maaş": "burs_maas"
}
KATEGORI_KOD_TO_GORUNUM = {v: k for k, v in KATEGORI_GORUNUM_TO_KOD.items()}


class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker - Kişisel Bütçe ve Harcama Takip")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f4f6f9")

        self.aktif_kullanici = None  # Giriş yapan kullanıcının sözlük (dict) verisi
        self.guncel_ay = datetime.now().strftime("%Y-%m")  # Örn: "2026-11"
        self.veriler = self.baslangic_verisi_al()
        self.giris_ekrani_olustur()

    def baslangic_verisi_al(self):
        if VERI_MODULU_AKTIF and hasattr(vm, "verileri_yukle"):
            yuklenen = vm.verileri_yukle()
            if yuklenen and "kullanicilar" in yuklenen:
                return yuklenen

        # Beyza'nın ortak JSON şemasına birebir uygun başlangıç/test verisi
        return {
            "kullanicilar": [
                {
                    "id": 1,
                    "kullanici_adi": "Enise Havva",
                    "eposta": "enise@mail.com",
                    "sifre": "1234",
                    "rozetler": ["Düzenli Kayıtçı"]
                }
            ],
            "islemler": [
                {"id": 1, "kullanici_id": 1, "tur": "gelir", "tutar": 5000.00, "kategori": "burs_maas", "tarih": "2026-11-01", "aciklama": "KYK Bursu"},
                {"id": 2, "kullanici_id": 1, "tur": "gider", "tutar": 850.00, "kategori": "market", "tarih": "2026-11-10", "aciklama": "Haftalık mutfak"},
                {"id": 3, "kullanici_id": 1, "tur": "gider", "tutar": 820.00, "kategori": "eglence", "tarih": "2026-11-15", "aciklama": "Sinema ve kafe"}
            ],
            "butce_limitleri": [
                {"kullanici_id": 1, "kategori": "market", "ay": self.guncel_ay, "limit_tutari": 1500.00},
                {"kullanici_id": 1, "kategori": "ulasim", "ay": self.guncel_ay, "limit_tutari": 600.00},
                {"kullanici_id": 1, "kategori": "fatura", "ay": self.guncel_ay, "limit_tutari": 1000.00},
                {"kullanici_id": 1, "kategori": "eglence", "ay": self.guncel_ay, "limit_tutari": 1000.00},
                {"kullanici_id": 1, "kategori": "egitim", "ay": self.guncel_ay, "limit_tutari": 800.00}
            ],
            "tasarruf_hedefleri": [
                {"id": 1, "kullanici_id": 1, "baslik": "Yeni laptop", "hedef_tutar": 25000.00, "birikmis_tutar": 7500.00, "tamamlandi_mi": False}
            ]
        }

    def degisiklikleri_kaydet(self):
        if VERI_MODULU_AKTIF and hasattr(vm, "verileri_kaydet"):
            vm.verileri_kaydet(self.veriler)

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

        tk.Label(cerceve, text="Kullanıcı Adı (Kayıt İçin):", bg="white", anchor="w").pack(fill="x")
        self.ent_ad = ttk.Entry(cerceve, width=35)
        self.ent_ad.pack(pady=(2, 10))

        tk.Label(cerceve, text="E-posta:", bg="white", anchor="w").pack(fill="x")
        self.ent_eposta = ttk.Entry(cerceve, width=35)
        self.ent_eposta.insert(0, "enise@mail.com")
        self.ent_eposta.pack(pady=(2, 10))

        tk.Label(cerceve, text="Şifre:", bg="white", anchor="w").pack(fill="x")
        self.ent_sifre = ttk.Entry(cerceve, width=35, show="*")
        self.ent_sifre.insert(0, "1234")
        self.ent_sifre.pack(pady=(2, 20))

        btn_frame = tk.Frame(cerceve, bg="white")
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Giriş Yap", bg="#2980b9", fg="white", font=("Segoe UI", 10, "bold"), width=14, command=self.giris_yap_tiklandi).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Kayıt Ol", bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), width=14, command=self.kayit_ol_tiklandi).pack(side="right", padx=5)

    def giris_yap_tiklandi(self):
        eposta = self.ent_eposta.get().strip()
        sifre = self.ent_sifre.get().strip()

        for kullanici in self.veriler["kullanicilar"]:
            if kullanici["eposta"] == eposta and kullanici["sifre"] == sifre:
                self.aktif_kullanici = kullanici
                self.ana_ekran_olustur()
                return

        messagebox.showerror("Giriş Hatası", "Hatalı e-posta veya şifre girdiniz!")

    def kayit_ol_tiklandi(self):
        ad = self.ent_ad.get().strip()
        eposta = self.ent_eposta.get().strip()
        sifre = self.ent_sifre.get().strip()

        if not ad or not eposta or not sifre:
            messagebox.showwarning("Eksik Bilgi", "Kayıt için tüm alanları doldurmalısınız.")
            return

        if any(k["eposta"] == eposta for k in self.veriler["kullanicilar"]):
            messagebox.showerror("Kayıt Hatası", "Bu e-posta adresi ile zaten kayıt olunmuş!")
            return

        yeni_id = max([k["id"] for k in self.veriler["kullanicilar"]], default=0) + 1
        yeni_kullanici = {
            "id": yeni_id,
            "kullanici_adi": ad,
            "eposta": eposta,
            "sifre": sifre,
            "rozetler": []
        }
        self.veriler["kullanicilar"].append(yeni_kullanici)
        self.degisiklikleri_kaydet()
        messagebox.showinfo("Başarılı", "Kayıt tamamlandı! Şimdi giriş yapabilirsiniz.")

    # ==========================================
    # 2. ANA KONTROL PANELİ (DASHBOARD)
    # ==========================================
    def ana_ekran_olustur(self):
        self.ekrani_temizle()

        ust_bar = tk.Frame(self.root, bg="#2c3e50", height=60, padx=20)
        ust_bar.pack(fill="x")

        tk.Label(ust_bar, text=f"Hoş Geldin, {self.aktif_kullanici['kullanici_adi']}", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white").pack(side="left", pady=15)
        self.lbl_bakiye = tk.Label(ust_bar, text="Güncel Bakiye: 0.00 TL", font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="#2ecc71")
        self.lbl_bakiye.pack(side="left", padx=40)
        tk.Button(ust_bar, text="Çıkış Yap", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=self.giris_ekrani_olustur).pack(side="right", pady=15)

        self.uyari_alani = tk.Frame(self.root, bg="#f4f6f9", padx=20, pady=5)
        self.uyari_alani.pack(fill="x")

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
    # SEKME 1: İŞLEM EKLEME, SİLME VE FİLTRELEME
    # ==========================================
    def islemler_sekmesini_doldur(self):
        form = tk.LabelFrame(self.sekme_islemler, text="Yeni İşlem Ekle", bg="white", padx=10, pady=10)
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Tür:", bg="white").grid(row=0, column=0, padx=5)
        self.cmb_tur = ttk.Combobox(form, values=["gider", "gelir"], width=9, state="readonly")
        self.cmb_tur.set("gider")
        self.cmb_tur.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Tutar (TL):", bg="white").grid(row=0, column=2, padx=5)
        self.ent_tutar = ttk.Entry(form, width=11)
        self.ent_tutar.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Kategori:", bg="white").grid(row=0, column=4, padx=5)
        self.cmb_kategori = ttk.Combobox(form, values=list(KATEGORI_GORUNUM_TO_KOD.keys()), width=13, state="readonly")
        self.cmb_kategori.set("Market")
        self.cmb_kategori.grid(row=0, column=5, padx=5)

        tk.Label(form, text="Açıklama:", bg="white").grid(row=0, column=6, padx=5)
        self.ent_aciklama = ttk.Entry(form, width=20)
        self.ent_aciklama.grid(row=0, column=7, padx=5)

        tk.Button(form, text="+ Ekle", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=10, command=self.islem_ekle).grid(row=0, column=8, padx=10)

        filtre_bar = tk.Frame(self.sekme_islemler, bg="white", pady=5)
        filtre_bar.pack(fill="x")
        tk.Label(filtre_bar, text="Kategori Filtresi:", bg="white").pack(side="left")
        self.cmb_filtre_kat = ttk.Combobox(filtre_bar, values=["Tümü"] + list(KATEGORI_GORUNUM_TO_KOD.keys()), width=14, state="readonly")
        self.cmb_filtre_kat.set("Tümü")
        self.cmb_filtre_kat.pack(side="left", padx=8)
        self.cmb_filtre_kat.bind("<<ComboboxSelected>>", lambda e: self.ekrani_guncelle())

        kolonlar = ("id", "tarih", "tur", "kategori", "tutar", "aciklama")
        self.tablo = ttk.Treeview(self.sekme_islemler, columns=kolonlar, show="headings", height=11)
        for kol, baslik in zip(kolonlar, ["ID", "Tarih", "Tür", "Kategori", "Tutar (TL)", "Açıklama"]):
            self.tablo.heading(kol, text=baslik)
            self.tablo.column(kol, width=110 if kol != "aciklama" else 230, anchor="center")
        self.tablo.pack(fill="both", expand=True)

        self.lbl_bos_liste = tk.Label(self.sekme_islemler, text="", bg="white", fg="#7f8c8d", font=("Segoe UI", 10, "italic"))
        self.lbl_bos_liste.pack(pady=4)

        tk.Button(self.sekme_islemler, text="Seçili İşlemi Sil", bg="#c0392b", fg="white", command=self.islem_sil).pack(anchor="e", pady=5)

    def islem_ekle(self):
        tutar_metni = self.ent_tutar.get().strip()
        try:
            tutar = round(float(tutar_metni.replace(",", ".")), 2)
            if tutar <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Geçersiz Tutar", "Tutar sıfırdan büyük sayısal bir değer olmalıdır!")
            return

        yeni_id = max([i["id"] for i in self.veriler["islemler"]], default=0) + 1
        secilen_gorunum = self.cmb_kategori.get()

        yeni_islem = {
            "id": yeni_id,
            "kullanici_id": self.aktif_kullanici["id"],
            "tur": self.cmb_tur.get(),
            "tutar": tutar,
            "kategori": KATEGORI_GORUNUM_TO_KOD[secilen_gorunum],
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "aciklama": self.ent_aciklama.get().strip() or "-"
        }
        self.veriler["islemler"].append(yeni_islem)
        self.degisiklikleri_kaydet()
        self.ent_tutar.delete(0, tk.END)
        self.ent_aciklama.delete(0, tk.END)
        self.ekrani_guncelle()

    def islem_sil(self):
        secili = self.tablo.selection()
        if not secili:
            messagebox.showwarning("Seçim Yok", "Silmek için tablodan bir işlem seçin.")
            return
        islem_id = self.tablo.item(secili[0])["values"][0]
        self.veriler["islemler"] = [i for i in self.veriler["islemler"] if i["id"] != islem_id]
        self.degisiklikleri_kaydet()
        self.ekrani_guncelle()

    # ==========================================
    # SEKME 2: BÜTÇE LİMİTLERİ (AY BAZLI) VE ÖZET
    # ==========================================
    def butce_sekmesini_doldur(self):
        sol = tk.LabelFrame(self.sekme_butce, text=f"Kategori Limiti Belirle ({self.guncel_ay})", bg="white", padx=15, pady=15)
        sol.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(sol, text="Kategori:", bg="white").pack(anchor="w")
        gider_kategorileri = [k for k in KATEGORI_GORUNUM_TO_KOD.keys() if k != "Burs / Maaş"]
        self.cmb_limit_kat = ttk.Combobox(sol, values=gider_kategorileri, state="readonly")
        self.cmb_limit_kat.set("Market")
        self.cmb_limit_kat.pack(fill="x", pady=(2, 10))

        tk.Label(sol, text="Aylık Limit Tutarı (TL):", bg="white").pack(anchor="w")
        self.ent_limit_tutar = ttk.Entry(sol)
        self.ent_limit_tutar.pack(fill="x", pady=(2, 10))

        tk.Button(sol, text="Limiti Kaydet / Güncelle", bg="#2980b9", fg="white", command=self.limit_guncelle).pack(fill="x")

        self.lbl_limit_listesi = tk.Label(sol, text="", bg="white", justify="left", font=("Segoe UI", 10))
        self.lbl_limit_listesi.pack(anchor="w", pady=15)

        sag = tk.LabelFrame(self.sekme_butce, text=f"Aylık Özet ve Kategori Dağılımı ({self.guncel_ay})", bg="white", padx=15, pady=15)
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

        kat_kodu = KATEGORI_GORUNUM_TO_KOD[self.cmb_limit_kat.get()]
        kid = self.aktif_kullanici["id"]

        # Mevcut ay ve kategori için limit varsa güncelle, yoksa yeni ekle
        bulundu = False
        for lim in self.veriler["butce_limitleri"]:
            if lim["kullanici_id"] == kid and lim["kategori"] == kat_kodu and lim["ay"] == self.guncel_ay:
                lim["limit_tutari"] = yeni_limit
                bulundu = True
                break

        if not bulundu:
            self.veriler["butce_limitleri"].append({
                "kullanici_id": kid,
                "kategori": kat_kodu,
                "ay": self.guncel_ay,
                "limit_tutari": yeni_limit
            })

        self.degisiklikleri_kaydet()
        self.ent_limit_tutar.delete(0, tk.END)
        self.ekrani_guncelle()

    # ==========================================
    # SEKME 3: TASARRUF HEDEFLERİ VE ROZETLER
    # ==========================================
    def hedefler_sekmesini_doldur(self):
        ust = tk.LabelFrame(self.sekme_hedefler, text="Tasarruf Hedeflerim", bg="white", padx=15, pady=15)
        ust.pack(fill="x", pady=(0, 15))

        # Yeni Hedef Ekleme Satırı
        hedef_form = tk.Frame(ust, bg="white")
        hedef_form.pack(fill="x", pady=(0, 10))
        tk.Label(hedef_form, text="Hedef Başlığı:", bg="white").pack(side="left")
        self.ent_hedef_baslik = ttk.Entry(hedef_form, width=22)
        self.ent_hedef_baslik.pack(side="left", padx=5)
        tk.Label(hedef_form, text="Hedef Tutar (TL):", bg="white").pack(side="left")
        self.ent_hedef_tutar = ttk.Entry(hedef_form, width=12)
        self.ent_hedef_tutar.pack(side="left", padx=5)
        tk.Button(hedef_form, text="+ Hedef Oluştur", bg="#27ae60", fg="white", command=self.hedef_ekle).pack(side="left", padx=8)

        self.hedef_cercevesi = tk.Frame(ust, bg="white")
        self.hedef_cercevesi.pack(fill="x")

        alt = tk.LabelFrame(self.sekme_hedefler, text="Kazanılan Rozetlerim", bg="white", padx=15, pady=15)
        alt.pack(fill="both", expand=True)

        self.lbl_rozetler = tk.Label(alt, text="", bg="white", font=("Segoe UI", 11, "bold"), fg="#8e44ad", justify="left")
        self.lbl_rozetler.pack(anchor="w")

    def hedef_ekle(self):
        baslik = self.ent_hedef_baslik.get().strip()
        try:
            tutar = round(float(self.ent_hedef_tutar.get().replace(",", ".")), 2)
            if not baslik or tutar <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir hedef başlığı ve pozitif tutar girin.")
            return

        yeni_id = max([h["id"] for h in self.veriler["tasarruf_hedefleri"]], default=0) + 1
        self.veriler["tasarruf_hedefleri"].append({
            "id": yeni_id,
            "kullanici_id": self.aktif_kullanici["id"],
            "baslik": baslik,
            "hedef_tutar": tutar,
            "birikmis_tutar": 0.00,
            "tamamlandi_mi": False
        })
        self.degisiklikleri_kaydet()
        self.ent_hedef_baslik.delete(0, tk.END)
        self.ent_hedef_tutar.delete(0, tk.END)
        self.ekrani_guncelle()

    def hedefe_para_ekle(self, hedef_id, miktar=500.00):
        for h in self.veriler["tasarruf_hedefleri"]:
            if h["id"] == hedef_id and not h["tamamlandi_mi"]:
                h["birikmis_tutar"] = round(h["birikmis_tutar"] + miktar, 2)
                if h["birikmis_tutar"] >= h["hedef_tutar"]:
                    h["tamamlandi_mi"] = True
                    if "Hedef Avcısı" not in self.aktif_kullanici["rozetler"]:
                        self.aktif_kullanici["rozetler"].append("Hedef Avcısı")
                        messagebox.showinfo("Tebrikler!", f"'{h['baslik']}' hedefine ulaştınız ve 'Hedef Avcısı' rozeti kazandınız!")
                break
        self.degisiklikleri_kaydet()
        self.ekrani_guncelle()

    # ==========================================
    # TÜM EKRAN VERİLERİNİ VE UYARILARI GÜNCELLEME
    # ==========================================
    def ekrani_guncelle(self):
        kid = self.aktif_kullanici["id"]
        kullanici_islemleri = [i for i in self.veriler["islemler"] if i["kullanici_id"] == kid]

        # Tabloyu Yenile
        for satir in self.tablo.get_children():
            self.tablo.delete(satir)

        secili_filtre_gorunum = self.cmb_filtre_kat.get()
        gosterilecek = [
            i for i in kullanici_islemleri
            if secili_filtre_gorunum == "Tümü" or i["kategori"] == KATEGORI_GORUNUM_TO_KOD[secili_filtre_gorunum]
        ]

        if not gosterilecek:
            self.lbl_bos_liste.config(text="Henüz kayıtlı işleminiz yok.")
        else:
            self.lbl_bos_liste.config(text="")
            for i in sorted(gosterilecek, key=lambda x: x["tarih"], reverse=True):
                kat_gorunum = KATEGORI_KOD_TO_GORUNUM.get(i["kategori"], i["kategori"])
                self.tablo.insert("", tk.END, values=(i["id"], i["tarih"], i["tur"].upper(), kat_gorunum, f"{i['tutar']:.2f}", i["aciklama"]))

        # Bakiye ve Seçili Ay Özeti
        aylik_islemler = [i for i in kullanici_islemleri if i["tarih"].startswith(self.guncel_ay)]
        toplam_gelir = sum(i["tutar"] for i in aylik_islemler if i["tur"] == "gelir")
        toplam_gider = sum(i["tutar"] for i in aylik_islemler if i["tur"] == "gider")
        kalan = toplam_gelir - toplam_gider

        self.lbl_bakiye.config(text=f"Güncel Bakiye: {kalan:.2f} TL")

        dagilim_metni = "\nKategori Harcama Dağılımı:\n"
        if toplam_gider > 0:
            kategoriler = set(i["kategori"] for i in aylik_islemler if i["tur"] == "gider")
            for k in sorted(kategoriler):
                k_toplam = sum(i["tutar"] for i in aylik_islemler if i["tur"] == "gider" and i["kategori"] == k)
                yuzde = (k_toplam / toplam_gider) * 100
                dagilim_metni += f"• {KATEGORI_KOD_TO_GORUNUM.get(k, k)}: {k_toplam:.2f} TL (%{yuzde:.1f})\n"
        else:
            dagilim_metni += "• Bu ay henüz gider kaydı bulunmuyor.\n"

        self.lbl_aylik_ozet.config(
            text=f"Toplam Gelir: {toplam_gelir:.2f} TL\n"
                 f"Toplam Gider: {toplam_gider:.2f} TL\n"
                 f"Kalan Bakiye: {kalan:.2f} TL\n"
                 f"{dagilim_metni}"
        )

        # Limit Kontrolleri (%80 Sarı / %100 Kırmızı Uyarı)
        for w in self.uyari_alani.winfo_children():
            w.destroy()

        kullanici_limitleri = [l for l in self.veriler["butce_limitleri"] if l["kullanici_id"] == kid and l["ay"] == self.guncel_ay]
        limit_metni = f"{self.guncel_ay} Dönemi Limitleri:\n"

        for lim in kullanici_limitleri:
            kat_kodu = lim["kategori"]
            kat_adi = KATEGORI_KOD_TO_GORUNUM.get(kat_kodu, kat_kodu)
            limit_tutari = lim["limit_tutari"]
            harcanan = sum(i["tutar"] for i in aylik_islemler if i["tur"] == "gider" and i["kategori"] == kat_kodu)

            limit_metni += f"• {kat_adi}: {harcanan:.2f} / {limit_tutari:.2f} TL\n"

            if harcanan > limit_tutari:
                asim = harcanan - limit_tutari
                tk.Label(self.uyari_alani, text=f"KIRMIZI UYARI: {kat_adi} kategorisi limiti {asim:.2f} TL aşıldı!", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(fill="x", pady=2)
            elif harcanan >= limit_tutari * 0.80:
                tk.Label(self.uyari_alani, text=f"SARI UYARI: {kat_adi} kategorisi harcamanız limitin %80'ine ulaştı ({harcanan:.2f}/{limit_tutari:.2f} TL).", bg="#f1c40f", fg="black", font=("Segoe UI", 9, "bold"), padx=10, pady=4).pack(fill="x", pady=2)

        self.lbl_limit_listesi.config(text=limit_metni)

        # Tasarruf Hedefleri İlerleme Çubuğu ve +500 TL Para Ayırma Butonu
        for w in self.hedef_cercevesi.winfo_children():
            w.destroy()

        kullanici_hedefleri = [h for h in self.veriler["tasarruf_hedefleri"] if h["kullanici_id"] == kid]
        for h in kullanici_hedefleri:
            satir_frame = tk.Frame(self.hedef_cercevesi, bg="white")
            satir_frame.pack(fill="x", pady=5)

            oran = min(100, (h["birikmis_tutar"] / h["hedef_tutar"]) * 100)
            durum = " [TAMAMLANDI]" if h["tamamlandi_mi"] else ""
            tk.Label(satir_frame, text=f"{h['baslik']}{durum} - {h['birikmis_tutar']:.2f} / {h['hedef_tutar']:.2f} TL (%{oran:.1f})", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")

            alt_satir = tk.Frame(satir_frame, bg="white")
            alt_satir.pack(fill="x", pady=2)
            bar = ttk.Progressbar(alt_satir, length=380, mode="determinate", value=oran)
            bar.pack(side="left")

            if not h["tamamlandi_mi"]:
                tk.Button(alt_satir, text="+500 TL Ayır", bg="#2980b9", fg="white", font=("Segoe UI", 8, "bold"), command=lambda hid=h["id"]: self.hedefe_para_ekle(hid, 500.0)).pack(side="left", padx=10)

        rozetler = self.aktif_kullanici["rozetler"]
        rozet_metni = "\n".join([f"🏆 {r}" for r in rozetler]) if rozetler else "Henüz kazanılmış rozet yok."
        self.lbl_rozetlefwr.config(text=rozet_metni)