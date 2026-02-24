import requests
import config


def optimize_route(locations):
    """
    Google Maps Directions API ile rota optimizasyonu.
    locations: [{'lat': float, 'lng': float, 'name': str}, ...]
    Returns: optimized order indices and total duration/distance
    """
    if not config.GOOGLE_MAPS_API_KEY or len(locations) < 2:
        return {'order': list(range(len(locations))), 'optimized': False}

    origin = f"{locations[0]['lat']},{locations[0]['lng']}"
    destination = f"{locations[-1]['lat']},{locations[-1]['lng']}"
    waypoints = '|'.join([f"{loc['lat']},{loc['lng']}" for loc in locations[1:-1]])

    url = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {
        'origin': origin,
        'destination': destination,
        'waypoints': f'optimize:true|{waypoints}' if waypoints else '',
        'key': config.GOOGLE_MAPS_API_KEY,
        'language': 'tr',
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data['status'] == 'OK':
            route = data['routes'][0]
            order = [0] + [i + 1 for i in route.get('waypoint_order', [])] + [len(locations) - 1]
            total_distance = sum(leg['distance']['value'] for leg in route['legs'])
            total_duration = sum(leg['duration']['value'] for leg in route['legs'])

            return {
                'order': order,
                'optimized': True,
                'total_distance_km': round(total_distance / 1000, 1),
                'total_duration_min': round(total_duration / 60),
            }
    except Exception:
        pass

    return {'order': list(range(len(locations))), 'optimized': False}


def geocode_address(address):
    """Adres -> (latitude, longitude) donusumu. Google Geocoding API kullanir."""
    if not config.GOOGLE_MAPS_API_KEY or not address:
        return None, None

    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': config.GOOGLE_MAPS_API_KEY,
        'language': 'tr',
        'region': 'tr',
        'components': 'country:TR'
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data['status'] == 'OK' and data['results']:
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
    except Exception:
        pass

    return None, None
