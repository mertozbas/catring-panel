import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from strands import tool

API_BASE = config.API_BASE


@tool
def get_todays_orders() -> str:
    """Bugünkü siparişleri getirir."""
    try:
        resp = requests.get(f"{API_BASE}/orders", timeout=5)
        orders = resp.json()
        if not orders:
            return "Bugün için sipariş bulunmuyor."
        lines = []
        for o in orders:
            lines.append(f"- {o['customer_name']}: {o['portion_count']} porsiyon ({o['container_type']})")
        return f"Bugünkü siparişler ({len(orders)} adet):\n" + "\n".join(lines)
    except Exception as e:
        return f"Siparişler alınamadı: {str(e)}"


@tool
def create_order(customer_name: str, portion_count: int, container_type: str = "sefer_tasi",
                 variety_count: int = 4, special_notes: str = "", date: str = "") -> str:
    """Yeni sipariş oluşturur.

    Args:
        customer_name: Müşteri/firma adı
        portion_count: Porsiyon sayısı
        container_type: Kap tipi (sefer_tasi, paket, kuvet, tepsi, poset)
        variety_count: Yemek çeşit sayısı
        special_notes: Özel notlar
        date: Sipariş tarihi (YYYY-MM-DD)
    """
    try:
        # Önce müşteriyi bul
        resp = requests.get(f"{API_BASE}/customers/search", params={"q": customer_name}, timeout=5)
        customers = resp.json()

        if not customers:
            return f"'{customer_name}' adında müşteri bulunamadı. Lütfen doğru firma adını belirtin."

        customer = customers[0]
        from datetime import date as dt
        order_date = date if date else dt.today().isoformat()

        order_data = {
            "date": order_date,
            "customer_id": customer["id"],
            "variety_count": variety_count,
            "portion_count": portion_count,
            "container_type": container_type,
            "special_notes": special_notes,
        }

        resp = requests.post(f"{API_BASE}/orders", json=order_data, timeout=5)
        result = resp.json()
        return f"Sipariş oluşturuldu! {customer['name']} için {portion_count} porsiyon ({container_type}), tarih: {order_date}"
    except Exception as e:
        return f"Sipariş oluşturulamadı: {str(e)}"


@tool
def get_daily_summary(date: str = "") -> str:
    """Günlük sipariş özetini getirir.

    Args:
        date: Tarih (YYYY-MM-DD), boş bırakılırsa bugün
    """
    try:
        from datetime import date as dt
        target_date = date if date else dt.today().isoformat()
        resp = requests.get(f"{API_BASE}/summary/{target_date}", timeout=5)
        data = resp.json()
        return (f"{target_date} Özeti:\n"
                f"Toplam sipariş: {data.get('total_orders', 0)}\n"
                f"Toplam porsiyon: {data.get('total_portions', 0)}\n"
                f"Sefer tası: {data.get('sefer_tasi', 0)}\n"
                f"Paket: {data.get('paket', 0)}\n"
                f"Küvet: {data.get('kuvet', 0)}\n"
                f"Tepsi: {data.get('tepsi', 0)}\n"
                f"Poşet: {data.get('poset', 0)}")
    except Exception as e:
        return f"Özet alınamadı: {str(e)}"
