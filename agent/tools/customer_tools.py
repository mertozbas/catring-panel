import requests
from strands import tool

API_BASE = "http://localhost:5050/api"


@tool
def search_customer(name: str) -> str:
    """Müşteri/firma arar.

    Args:
        name: Aranacak firma adı
    """
    try:
        resp = requests.get(f"{API_BASE}/customers/search", params={"q": name}, timeout=5)
        customers = resp.json()
        if not customers:
            return f"'{name}' ile eşleşen müşteri bulunamadı."
        lines = []
        for c in customers:
            lines.append(f"- {c['name']} | Kap: {c['default_container_type']} | Çeşit: {c['default_variety_count']}")
            if c.get('special_notes'):
                lines.append(f"  Not: {c['special_notes']}")
        return f"Bulunan müşteriler:\n" + "\n".join(lines)
    except Exception as e:
        return f"Arama yapılamadı: {str(e)}"


@tool
def list_customers() -> str:
    """Tüm aktif müşterileri listeler."""
    try:
        resp = requests.get(f"{API_BASE}/customers", timeout=5)
        customers = resp.json()
        if not customers:
            return "Kayıtlı müşteri yok."
        lines = [f"Toplam {len(customers)} müşteri:"]
        for c in customers:
            lines.append(f"- {c['name']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Müşteri listesi alınamadı: {str(e)}"


@tool
def register_customer(name: str, contact_name: str = "", phone: str = "",
                      default_portion_count: int = 0, default_container_type: str = "sefer_tasi",
                      special_notes: str = "") -> str:
    """Yeni müşteri kaydeder.

    Args:
        name: Firma adı
        contact_name: İletişim kişisi adı
        phone: Telefon numarası
        default_portion_count: Varsayılan porsiyon sayısı
        default_container_type: Varsayılan kap tipi
        special_notes: Özel notlar
    """
    try:
        data = {
            "name": name,
            "contact_name": contact_name,
            "phone": phone,
            "default_portion_count": default_portion_count,
            "default_container_type": default_container_type,
            "special_notes": special_notes,
        }
        resp = requests.post(f"{API_BASE}/customers", json=data, timeout=5)
        result = resp.json()
        return f"Müşteri kaydedildi: {name}"
    except Exception as e:
        return f"Müşteri kaydedilemedi: {str(e)}"
