import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from strands import tool

API_BASE = config.API_BASE


@tool
def get_route_status(date: str = "") -> str:
    """Rota durumlarini getirir - teslimat takibi.

    Args:
        date: Tarih (YYYY-MM-DD), bos birakilirsa bugun
    """
    try:
        from datetime import date as dt
        target_date = date if date else dt.today().isoformat()
        resp = requests.get(f"{API_BASE}/routes", params={"date": target_date}, timeout=5)
        routes = resp.json()
        if not routes:
            return f"{target_date} tarihinde rota bulunmuyor."

        lines = [f"Rota Durumu ({target_date}):"]
        for r in routes:
            status_icon = "✅" if r.get('status') == 'completed' else "🔄" if r.get('status') == 'in_progress' else "📋"
            lines.append(f"{status_icon} {r.get('route_name', r.get('driver_name', '?'))}: "
                        f"{r.get('total_portions', 0)} porsiyon - {r.get('status', '?')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Rota durumu alinamadi: {str(e)}"


@tool
def get_delivery_tracking(customer_name: str = "") -> str:
    """Teslimat takibi - musteri bazli veya genel.

    Args:
        customer_name: Musteri adi (bos birakilirsa genel ozet)
    """
    try:
        from datetime import date as dt
        today = dt.today().isoformat()
        resp = requests.get(f"{API_BASE}/orders", params={"date": today}, timeout=5)
        orders = resp.json()
        if not orders:
            return "Bugun siparis bulunmuyor."

        if customer_name:
            filtered = [o for o in orders if customer_name.lower() in o.get('customer_name', '').lower()]
            if not filtered:
                return f"'{customer_name}' icin bugun siparis bulunamadi."
            lines = [f"{customer_name} Teslimat Durumu:"]
            for o in filtered:
                icon = "✅" if o['status'] == 'delivered' else "⏳" if o['status'] == 'pending' else "🍳" if o['status'] == 'preparing' else "📦"
                lines.append(f"{icon} {o['portion_count']} porsiyon ({o.get('container_type', '?')}) - {o['status']}")
            return "\n".join(lines)

        # Genel ozet
        delivered = sum(1 for o in orders if o['status'] == 'delivered')
        total = len(orders)
        lines = [f"Teslimat Ozeti ({today}):",
                 f"Toplam: {total} siparis",
                 f"Teslim edilen: {delivered}",
                 f"Bekleyen: {total - delivered}"]
        return "\n".join(lines)
    except Exception as e:
        return f"Teslimat takibi alinamadi: {str(e)}"
