from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path

VERI_DOSYASI = Path("data/veriler.json")

VARSAYILAN_VERILER = {
    "kullanicilar": [],
    "islemler": [],
    "limitler": [],
    "hedefler": [],
}


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