import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from strands import tool

API_BASE = config.API_BASE


@tool
def get_daily_report_summary(date: str = "") -> str:
    """Gunluk ozet raporu - siparis, porsiyon, teslimat, kap dagilimi.

    Args:
        date: Tarih (YYYY-MM-DD), bos birakilirsa bugun
    """
    try:
        from datetime import date as dt
        target_date = date if date else dt.today().isoformat()

        # Siparis ozeti
        resp = requests.get(f"{API_BASE}/summary/{target_date}", timeout=5)
        summary = resp.json()

        # Rota ozeti
        resp2 = requests.get(f"{API_BASE}/routes", params={"date": target_date}, timeout=5)
        routes = resp2.json()

        completed_routes = sum(1 for r in routes if r.get('status') == 'completed')

        lines = [
            f"📊 GUNLUK RAPOR - {target_date}",
            f"",
            f"📦 Siparis: {summary.get('total_orders', 0)}",
            f"🍽️ Porsiyon: {summary.get('total_portions', 0)}",
            f"🚛 Rota: {completed_routes}/{len(routes)} tamamlandi",
            f"",
            f"Kap Dagilimi:",
            f"  Sefer Tasi: {summary.get('sefer_tasi', 0)}",
            f"  Paket: {summary.get('paket', 0)}",
            f"  Kuvet: {summary.get('kuvet', 0)}",
            f"  Tepsi: {summary.get('tepsi', 0)}",
            f"  Poset: {summary.get('poset', 0)}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Rapor alinamadi: {str(e)}"


@tool
def get_weekly_summary() -> str:
    """Bu haftanin ozet raporunu getirir."""
    try:
        from datetime import date, timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        total_orders = 0
        total_portions = 0
        daily_lines = []

        for i in range(min(today.weekday() + 1, 7)):
            d = week_start + timedelta(days=i)
            date_str = d.isoformat()
            resp = requests.get(f"{API_BASE}/summary/{date_str}", timeout=5)
            summary = resp.json()
            orders = summary.get('total_orders', 0) or 0
            portions = summary.get('total_portions', 0) or 0
            total_orders += orders
            total_portions += portions
            day_names = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz']
            daily_lines.append(f"  {day_names[i]}: {orders} siparis, {portions} porsiyon")

        lines = [
            f"📊 HAFTALIK OZET",
            f"({week_start.isoformat()} - {today.isoformat()})",
            f"",
            f"Toplam Siparis: {total_orders}",
            f"Toplam Porsiyon: {total_portions}",
            f"",
            f"Gunluk Dagılım:",
        ] + daily_lines

        return "\n".join(lines)
    except Exception as e:
        return f"Haftalik ozet alinamadi: {str(e)}"
