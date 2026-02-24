import requests
from strands import tool

API_BASE = "http://localhost:5050/api"


@tool
def format_menu_for_telegram() -> str:
    """Haftalık menüyü Telegram'da paylaşım için formatlar."""
    try:
        resp = requests.get(f"{API_BASE}/menu/current", timeout=5)
        if resp.status_code == 404:
            return "Paylaşılacak menü bulunamadı."

        data = resp.json()
        lines = ["HAFTALIK YEMEK LİSTESİ", f"({data['week_start_date']} Haftası)", ""]

        for day, items in data.get('days', {}).items():
            lines.append(f"*{day}*")
            for item in items:
                lines.append(f"  {item}")
            lines.append("")

        lines.append("_Başak Yemek Catering - Afiyet Olsun!_")
        return "\n".join(lines)
    except Exception as e:
        return f"Menü formatlanamadı: {str(e)}"
