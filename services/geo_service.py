import requests

class GeoService:
    @staticmethod
    def get_currency_and_rates(client_ip):
        currency = 'USD'
        try:
            if client_ip in ['127.0.0.1', '::1', 'localhost']:
                client_ip = '8.8.8.8' # Fallback for local testing
            
            geo_res = requests.get(f'https://ipapi.co/{client_ip}/json/', timeout=3).json()
            currency = geo_res.get('currency', 'USD')
        except Exception:
            pass

        rates = {'USD': 1.0, 'ZAR': 18.50, 'EUR': 0.92, 'GBP': 0.79, 'JPY': 150.0}
        try:
            rate_res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=3).json()
            if 'rates' in rate_res:
                rates = rate_res['rates']
        except Exception:
            pass

        return currency, rates
