import requests

def get_usd_rate():
    try:
        response = requests.get('https://nbu.uz/uz/exchange-rates/json/')
        data = response.json()
        for item in data:
            if item['code'] == 'USD':
                return float(item['cb_price'])
    except Exception:
        return 12500.0
    return 12500.0