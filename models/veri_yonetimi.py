from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import re

PROJE_KOK_DIZINI = Path(__file__).resolve().parent.parent
VERI_DOSYASI = PROJE_KOK_DIZINI / "data" / "veriler.json"

VARSAYILAN_VERILER = {
    "kullanicilar": [],
    "islemler": [],
    "limitler": [],
    "hedefler": [],
}

EPOSTA_DESENI = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TARIH_DESENI = re.compile(r"^\d{4}-\d{2}-\d{2}$")
AY_DESENI = re.compile(r"^\d{4}-\d{2}$")
GECERLI_TURLER = {"gelir", "gider"}


def verileri_yukle(dosya_yolu: Path = VERI_DOSYASI) -> dict:
    """JSON dosyasindan verileri okur; dosya yoksa varsayilan yapiyi dondurur."""
    if not dosya_yolu.exists():
        return {
            "kullanicilar": [],
            "islemler": [],
            "limitler": [],
            "hedefler": [],
        }

    with dosya_yolu.open("r", encoding="utf-8") as dosya:
        veri = json.load(dosya)

    for anahtar in VARSAYILAN_VERILER:
        if anahtar not in veri or not isinstance(veri[anahtar], list):
            veri[anahtar] = []

    return veri


def verileri_kaydet(veri: dict, dosya_yolu: Path = VERI_DOSYASI) -> None:
    """Verileri UTF-8 formatinda JSON dosyasina kaydeder."""
    dosya_yolu.parent.mkdir(parents=True, exist_ok=True)
    with dosya_yolu.open("w", encoding="utf-8") as dosya:
        json.dump(veri, dosya, ensure_ascii=False, indent=2)


def tutar_dogrula_ve_yuvarla(tutar) -> tuple[bool, float | None, str]:
    """
    Tutari kontrol eder:
    - Sayisal olmalidir
    - 0 veya negatif olamaz
    - 2 ondalik basamaga yuvarlanir
    """
    if isinstance(tutar, bool) or tutar is None:
        return False, None, "Gecerli bir tutar giriniz."

    try:
        ondalik = Decimal(str(tutar).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        return False, None, "Tutar sayisal bir deger olmalidir."

    if ondalik.is_nan() or ondalik.is_infinite():
        return False, None, "Gecerli bir tutar giriniz."

    if ondalik <= Decimal("0"):
        return False, None, "Tutar sifirdan buyuk olmalidir."

    yuvarlanmis = float(ondalik.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return True, yuvarlanmis, ""


def kullanici_kaydet(
    kullanici_adi: str,
    eposta: str,
    sifre: str,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """
    Yeni kullanici kaydeder.
    - Bos alan kontrolu yapar
    - Gecerli e-posta ve asgari sifre uzunlugu kontrolu yapar
    - Ayni e-posta ile ikinci kaydi engeller
    """
    ad_temiz = (kullanici_adi or "").strip()
    eposta_temiz = (eposta or "").strip().lower()
    sifre_ham = sifre or ""

    if not ad_temiz or not eposta_temiz or not sifre_ham:
        return False, None, "Kullanici adi, e-posta ve sifre alanlari bos birakilamaz."

    if not EPOSTA_DESENI.match(eposta_temiz):
        return False, None, "Gecerli bir e-posta adresi giriniz."

    if len(sifre_ham) < 6:
        return False, None, "Sifre en az 6 karakter olmalidir."

    veri = verileri_yukle(dosya_yolu)

    for mevcut in veri["kullanicilar"]:
        if str(mevcut.get("eposta", "")).strip().lower() == eposta_temiz:
            return False, None, "Bu e-posta adresi ile zaten kayit olunmus."

    mevcut_idler = [
        k.get("id", 0) for k in veri["kullanicilar"] if isinstance(k.get("id"), int)
    ]
    yeni_id = max(mevcut_idler, default=0) + 1

    yeni_kullanici = {
        "id": yeni_id,
        "kullanici_adi": ad_temiz,
        "eposta": eposta_temiz,
        "sifre": sifre_ham,
        "rozetler": [],
    }

    veri["kullanicilar"].append(yeni_kullanici)
    verileri_kaydet(veri, dosya_yolu)

    return True, yeni_kullanici, "Kayit basariyla tamamlandi."


def kullanici_giris(
    eposta: str,
    sifre: str,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """E-posta ve sifre ile kullanici girisi yapar."""
    eposta_temiz = (eposta or "").strip().lower()
    sifre_ham = sifre or ""

    if not eposta_temiz or not sifre_ham:
        return False, None, "E-posta ve sifre alanlari bos birakilamaz."

    veri = verileri_yukle(dosya_yolu)

    for kullanici in veri["kullanicilar"]:
        kayitli_eposta = str(kullanici.get("eposta", "")).strip().lower()
        kayitli_sifre = kullanici.get("sifre", "")
        if kayitli_eposta == eposta_temiz and kayitli_sifre == sifre_ham:
            return True, kullanici, "Giris basarili."

    return False, None, "Hatali e-posta veya sifre."


def _tarih_dogrula(tarih: str | None) -> tuple[bool, str, str]:
    """Tarihi YYYY-MM-DD biciminde dogrular; bos ise bugunun tarihini dondurur."""
    if tarih is None or str(tarih).strip() == "":
        return True, datetime.now().strftime("%Y-%m-%d"), ""

    tarih_temiz = str(tarih).strip()
    if not TARIH_DESENI.match(tarih_temiz):
        return False, "", "Tarih YYYY-AA-GG biciminde olmalidir (orn. 2026-11-23)."

    try:
        datetime.strptime(tarih_temiz, "%Y-%m-%d")
    except ValueError:
        return False, "", "Gecerli bir takvim tarihi giriniz."

    return True, tarih_temiz, ""


def islem_ekle(
    kullanici_id: int,
    tur: str,
    tutar,
    kategori: str,
    tarih: str | None = None,
    aciklama: str = "",
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """Yeni gelir veya gider islemi ekler."""
    tur_temiz = (tur or "").strip().lower()
    if tur_temiz not in GECERLI_TURLER:
        return False, None, "Islem turu 'gelir' veya 'gider' olmalidir."

    tutar_gecerli, yuvarlanmis_tutar, tutar_mesaj = tutar_dogrula_ve_yuvarla(tutar)
    if not tutar_gecerli:
        return False, None, tutar_mesaj

    kategori_temiz = (kategori or "").strip().lower()
    if not kategori_temiz:
        return False, None, "Kategori alani bos birakilamaz."

    tarih_gecerli, tarih_temiz, tarih_mesaj = _tarih_dogrula(tarih)
    if not tarih_gecerli:
        return False, None, tarih_mesaj

    aciklama_temiz = (aciklama or "").strip()

    veri = verileri_yukle(dosya_yolu)
    mevcut_idler = [
        i.get("id", 0) for i in veri["islemler"] if isinstance(i.get("id"), int)
    ]
    yeni_id = max(mevcut_idler, default=0) + 1

    yeni_islem = {
        "id": yeni_id,
        "kullanici_id": kullanici_id,
        "tur": tur_temiz,
        "tutar": yuvarlanmis_tutar,
        "kategori": kategori_temiz,
        "tarih": tarih_temiz,
        "aciklama": aciklama_temiz,
    }

    veri["islemler"].append(yeni_islem)
    verileri_kaydet(veri, dosya_yolu)

    return True, yeni_islem, "Islem basariyla eklendi."


def islemleri_listele(
    kullanici_id: int,
    kategori: str | None = None,
    ay: str | None = None,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[list[dict], str]:
    """
    Kullanicinin islemlerini tarihe gore siralar ve istege bagli
    kategori veya ay ('YYYY-MM') bazinda filtreler.
    """
    veri = verileri_yukle(dosya_yolu)
    kayitlar = [
        i for i in veri["islemler"] if i.get("kullanici_id") == kullanici_id
    ]

    if kategori and str(kategori).strip():
        kategori_temiz = str(kategori).strip().lower()
        kayitlar = [
            i for i in kayitlar if str(i.get("kategori", "")).strip().lower() == kategori_temiz
        ]

    if ay and str(ay).strip():
        ay_temiz = str(ay).strip()
        if AY_DESENI.match(ay_temiz):
            kayitlar = [
                i for i in kayitlar if str(i.get("tarih", "")).startswith(ay_temiz)
            ]

    kayitlar.sort(key=lambda i: (str(i.get("tarih", "")), i.get("id", 0)), reverse=True)

    if not kayitlar:
        return [], "Henüz kayıtlı işleminiz yok"

    return kayitlar, ""


def islem_guncelle(
    kullanici_id: int,
    islem_id: int,
    tutar=None,
    kategori: str | None = None,
    tarih: str | None = None,
    aciklama: str | None = None,
    tur: str | None = None,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """Var olan bir islemin alanlarini gunceller."""
    veri = verileri_yukle(dosya_yolu)

    for islem in veri["islemler"]:
        if islem.get("id") == islem_id and islem.get("kullanici_id") == kullanici_id:
            if tur is not None:
                tur_temiz = str(tur).strip().lower()
                if tur_temiz not in GECERLI_TURLER:
                    return False, None, "Islem turu 'gelir' veya 'gider' olmalidir."
                islem["tur"] = tur_temiz

            if tutar is not None:
                tutar_gecerli, yuvarlanmis_tutar, tutar_mesaj = tutar_dogrula_ve_yuvarla(tutar)
                if not tutar_gecerli:
                    return False, None, tutar_mesaj
                islem["tutar"] = yuvarlanmis_tutar

            if kategori is not None:
                kategori_temiz = str(kategori).strip().lower()
                if not kategori_temiz:
                    return False, None, "Kategori alani bos birakilamaz."
                islem["kategori"] = kategori_temiz

            if tarih is not None:
                tarih_gecerli, tarih_temiz, tarih_mesaj = _tarih_dogrula(tarih)
                if not tarih_gecerli:
                    return False, None, tarih_mesaj
                islem["tarih"] = tarih_temiz

            if aciklama is not None:
                islem["aciklama"] = str(aciklama).strip()

            verileri_kaydet(veri, dosya_yolu)
            return True, islem, "Islem guncellendi."

    return False, None, "Guncellenecek islem bulunamadi."


def islem_sil(
    kullanici_id: int,
    islem_id: int,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, str]:
    """Belirtilen islemi listeden kaldirir ve JSON dosyasini gunceller."""
    veri = verileri_yukle(dosya_yolu)
    onceki_sayi = len(veri["islemler"])

    veri["islemler"] = [
        i
        for i in veri["islemler"]
        if not (i.get("id") == islem_id and i.get("kullanici_id") == kullanici_id)
    ]

    if len(veri["islemler"]) == onceki_sayi:
        return False, "Silinecek islem bulunamadi."

    verileri_kaydet(veri, dosya_yolu)
    return True, "Islem silindi."
def _ay_dogrula(ay: str | None) -> tuple[bool, str, str]:
    """Ayi YYYY-MM biciminde dogrular; bos ise icinde bulunulan ayi dondurur."""
    if ay is None or str(ay).strip() == "":
        return True, datetime.now().strftime("%Y-%m"), ""

    ay_temiz = str(ay).strip()
    if not AY_DESENI.match(ay_temiz):
        return False, "", "Ay bilgisi YYYY-AA biciminde olmalidir (orn. 2026-11)."

    try:
        datetime.strptime(f"{ay_temiz}-01", "%Y-%m-%d")
    except ValueError:
        return False, "", "Gecerli bir ay degeri giriniz."

    return True, ay_temiz, ""


def limit_belirle(
    kullanici_id: int,
    kategori: str,
    limit_tutari,
    ay: str | None = None,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """Kullanici, kategori ve ay icin aylik butce limiti ekler veya gunceller."""
    kategori_temiz = (kategori or "").strip().lower()
    if not kategori_temiz:
        return False, None, "Kategori alani bos birakilamaz."

    ay_gecerli, ay_temiz, ay_mesaj = _ay_dogrula(ay)
    if not ay_gecerli:
        return False, None, ay_mesaj

    tutar_gecerli, yuvarlanmis_limit, tutar_mesaj = tutar_dogrula_ve_yuvarla(limit_tutari)
    if not tutar_gecerli:
        return False, None, tutar_mesaj

    veri = verileri_yukle(dosya_yolu)

    for limit in veri["limitler"]:
        if (
            limit.get("kullanici_id") == kullanici_id
            and str(limit.get("kategori", "")).strip().lower() == kategori_temiz
            and str(limit.get("ay", "")).strip() == ay_temiz
        ):
            limit["limit_tutari"] = yuvarlanmis_limit
            verileri_kaydet(veri, dosya_yolu)
            return True, limit, "Butce limiti guncellendi."

    yeni_limit = {
        "kullanici_id": kullanici_id,
        "kategori": kategori_temiz,
        "ay": ay_temiz,
        "limit_tutari": yuvarlanmis_limit,
    }
    veri["limitler"].append(yeni_limit)
    verileri_kaydet(veri, dosya_yolu)

    return True, yeni_limit, "Butce limiti kaydedildi."


def limitleri_listele(
    kullanici_id: int,
    ay: str | None = None,
    dosya_yolu: Path = VERI_DOSYASI,
) -> list[dict]:
    """Kullanicinin tanimladigi butce limitlerini dondurur."""
    veri = verileri_yukle(dosya_yolu)
    kayitlar = [
        l for l in veri["limitler"] if l.get("kullanici_id") == kullanici_id
    ]

    if ay and str(ay).strip():
        ay_temiz = str(ay).strip()
        kayitlar = [l for l in kayitlar if str(l.get("ay", "")).strip() == ay_temiz]

    return kayitlar


def hedef_olustur(
    kullanici_id: int,
    baslik: str,
    hedef_tutar,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """Yeni tasarruf hedefi olusturur."""
    baslik_temiz = (baslik or "").strip()
    if not baslik_temiz:
        return False, None, "Hedef basligi bos birakilamaz."

    tutar_gecerli, yuvarlanmis_hedef, tutar_mesaj = tutar_dogrula_ve_yuvarla(hedef_tutar)
    if not tutar_gecerli:
        return False, None, tutar_mesaj

    veri = verileri_yukle(dosya_yolu)
    mevcut_idler = [
        h.get("id", 0) for h in veri["hedefler"] if isinstance(h.get("id"), int)
    ]
    yeni_id = max(mevcut_idler, default=0) + 1

    yeni_hedef = {
        "id": yeni_id,
        "kullanici_id": kullanici_id,
        "baslik": baslik_temiz,
        "hedef_tutar": yuvarlanmis_hedef,
        "birikmis_tutar": 0.0,
        "tamamlandi_mi": False,
    }

    veri["hedefler"].append(yeni_hedef)
    verileri_kaydet(veri, dosya_yolu)

    return True, yeni_hedef, "Tasarruf hedefi olusturuldu."


def hedefe_para_ayir(
    kullanici_id: int,
    hedef_id: int,
    eklenecek_tutar,
    dosya_yolu: Path = VERI_DOSYASI,
) -> tuple[bool, dict | None, str]:
    """Tasarruf hedefine para ekler; hedef tamamlanirsa durumu ve rozeti gunceller."""
    tutar_gecerli, yuvarlanmis_tutar, tutar_mesaj = tutar_dogrula_ve_yuvarla(eklenecek_tutar)
    if not tutar_gecerli:
        return False, None, tutar_mesaj

    veri = verileri_yukle(dosya_yolu)

    for hedef in veri["hedefler"]:
        if hedef.get("id") == hedef_id and hedef.get("kullanici_id") == kullanici_id:
            mevcut_birikmis = Decimal(str(hedef.get("birikmis_tutar", 0)))
            yeni_birikmis = float(
                (mevcut_birikmis + Decimal(str(yuvarlanmis_tutar))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            hedef_tutari = Decimal(str(hedef.get("hedef_tutar", 0)))

            hedef["birikmis_tutar"] = yeni_birikmis
            if Decimal(str(yeni_birikmis)) >= hedef_tutari:
                hedef["tamamlandi_mi"] = True
                for kullanici in veri["kullanicilar"]:
                    if kullanici.get("id") == kullanici_id:
                        rozetler = kullanici.setdefault("rozetler", [])
                        if "Hedef Avcısı" not in rozetler:
                            rozetler.append("Hedef Avcısı")
                        break

            verileri_kaydet(veri, dosya_yolu)
            return True, hedef, "Hedefe para ayrildi."

    return False, None, "Tasarruf hedefi bulunamadi."