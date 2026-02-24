from datetime import date, timedelta


def get_week_start(d=None):
    if d is None:
        d = date.today()
    elif isinstance(d, str):
        d = date.fromisoformat(d)
    return d - timedelta(days=d.weekday())


def get_week_dates(week_start):
    if isinstance(week_start, str):
        week_start = date.fromisoformat(week_start)
    return [week_start + timedelta(days=i) for i in range(6)]


def parse_portion_detail(detail):
    if not detail:
        return 0
    try:
        return sum(int(x.strip()) for x in detail.replace('+', ' ').split())
    except (ValueError, TypeError):
        return 0


CONTAINER_LABELS = {
    'sefer_tasi': 'Sefer Tası',
    'paket': 'Paket',
    'kuvet': 'Küvet',
    'tepsi': 'Tepsi',
    'poset': 'Poşet',
}

DAY_NAMES_TR = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
