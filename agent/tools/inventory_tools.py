import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from strands import tool

API_BASE = config.API_BASE


@tool
def get_stock_status(ingredient_name: str = "") -> str:
    """Stok durumunu sorgular.

    Args:
        ingredient_name: Malzeme adi (bos birakilirsa dusuk stoklar gosterilir)
    """
    try:
        resp = requests.get(f"{API_BASE}/inventory", timeout=5)
        items = resp.json()
        if not items:
            return "Envanter kaydi bulunmuyor."

        if ingredient_name:
            filtered = [i for i in items if ingredient_name.lower() in i.get('ingredient_name', '').lower()]
            if not filtered:
                return f"'{ingredient_name}' bulunamadi."
            lines = [f"Stok Durumu - {ingredient_name}:"]
            for i in filtered:
                status = "⚠️ DUSUK" if i.get('min_stock_level') and i['current_stock'] < i['min_stock_level'] else "✅"
                lines.append(f"{status} {i['ingredient_name']}: {i['current_stock']} {i['unit']}")
                if i.get('min_stock_level'):
                    lines.append(f"   Min: {i['min_stock_level']} {i['unit']}")
            return "\n".join(lines)

        # Dusuk stoklar
        low = [i for i in items if i.get('min_stock_level') and i['current_stock'] < i['min_stock_level']]
        if not low:
            return "Tum stoklar yeterli seviyede. ✅"

        lines = [f"⚠️ Dusuk Stok Uyarisi ({len(low)} kalem):"]
        for i in low:
            lines.append(f"  - {i['ingredient_name']}: {i['current_stock']}/{i['min_stock_level']} {i['unit']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Stok bilgisi alinamadi: {str(e)}"
