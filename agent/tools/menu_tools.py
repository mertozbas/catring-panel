import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from strands import tool

API_BASE = config.API_BASE


@tool
def get_current_menu() -> str:
    """Bu haftanın menüsünü getirir."""
    try:
        resp = requests.get(f"{API_BASE}/menu/current", timeout=5)
        if resp.status_code == 404:
            return "Bu hafta için menü henüz yayınlanmamış."
        data = resp.json()
        lines = [f"Bu Haftanın Menüsü ({data['week_start_date']} haftası):"]
        lines.append("")
        for day, items in data.get('days', {}).items():
            lines.append(f"{day}:")
            for item in items:
                lines.append(f"  - {item}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Menü alınamadı: {str(e)}"


@tool
def get_todays_menu() -> str:
    """Bugünün menüsünü getirir."""
    try:
        from datetime import date
        resp = requests.get(f"{API_BASE}/menu/current", timeout=5)
        if resp.status_code == 404:
            return "Bu hafta için menü henüz yayınlanmamış."
        data = resp.json()

        day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
        today_idx = date.today().weekday()
        if today_idx >= 6:
            return "Bugün Pazar, menü bulunmuyor."

        today_name = day_names[today_idx]
        items = data.get('days', {}).get(today_name, [])

        if not items:
            return f"Bugün ({today_name}) için menü bilgisi bulunamadı."

        lines = [f"Bugünün Menüsü ({today_name}):"]
        for item in items:
            lines.append(f"  - {item}")
        return "\n".join(lines)
    except Exception as e:
        return f"Menü alınamadı: {str(e)}"
