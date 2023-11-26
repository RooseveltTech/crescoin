import requests
from django.conf import settings
from main.models import CurrencyExchangeTable

exchange_rate_api_key = settings.EXCHANGE_RATE_API_KEY
def create_exchange_currency(exchange_rate_api_key):
    url = f"http://data.fixer.io/api/symbols?access_key={exchange_rate_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        rates = response_data.get("symbols")
        for key, value in rates.items():
            if not CurrencyExchangeTable.objects.filter(short_code=key).exists():
                CurrencyExchangeTable.objects.create(
                    short_code=key,
                    currency_name=value
                )
    else:
        return "failed to create exchange currency"
    
def update_exchange_rate(exchange_rate_api_key):
    url = f"http://data.fixer.io/api/latest?access_key={exchange_rate_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        rates = response_data.get("rates")
        for key, value in rates.items():
            CurrencyExchangeTable.objects.filter(short_code=key).update(currency_rate=value)
    else:
        return "failed to update exchange rate"
    
