import json
import requests
import os
from pprint import pprint
from time import sleep
from datetime import (
    datetime,
    date,
    timedelta,
    )
from urllib.parse import urlencode


class StockRequest:
    def __init__(self) -> None:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Combine the script directory with the 'key' file name
        key_path = os.path.join(script_dir, 'key')

        with open(key_path) as f:
            self.key = f.read()

        self.base_url = 'https://www.alphavantage.co/'

    def get_single_stock_prices(self, symbol: str, start_date: date=None, end_date: date=None) -> dict:
        data = {
            'function': 'TIME_SERIES_DAILY',
            'apikey': self.key,
            'symbol':symbol,
            'outputsize':'full'
        }

        params = urlencode(data)
        r = requests.get(url=f'{self.base_url}query?', params=data)
        response_json: dict = r.json()['Time Series (Daily)']
        
        if start_date is None and end_date is None:
            return response_json
        elif start_date is not None and end_date is None:
            return {k:response_json[k] for k in response_json if datetime.strptime(k, '%Y-%m-%d').date() <= start_date}
        elif start_date is None and end_date is not None:
            return {k:response_json[k] for k in response_json if datetime.strptime(k, '%Y-%m-%d').date() >= end_date}
        else:
            return {k:response_json[k] for k in response_json if end_date <= datetime.strptime(k, '%Y-%m-%d').date() <= start_date}


    def get_multiple_stock_prices(self, symbols: list[str], start_date: date=None, end_date: date=None) -> dict:
        """
        5 API requests per minute and 100 requests per day
        """

        response = dict({})

        for symbol in symbols:
            response[symbol] = self.get_single_stock_prices(symbol, start_date, end_date)
            sleep(12)

        return response
    
    def percent_diff_between_days(self, symbol: str, day1: date, day2: date) -> float:
        if day1 == day2:
            return 'Same date given'
        
        response1: dict = self.get_single_stock_prices(symbol=symbol, start_date=day1, end_date=day1)
        print('response1')
        pprint(response1)
        sleep(12)
        response2: dict = self.get_single_stock_prices(symbol=symbol, start_date=day2, end_date=day2)
        print('response2')
        pprint(response2)
        
        if len(response2) == 0:
            return f'{day2} has no entries'
        elif len(response1) == 0:
            return f'{day1} has no entries'

        close1 = float(response1[day1.strftime('%Y-%m-%d')]['4. close'])
        close2 = float(response2[day2.strftime('%Y-%m-%d')]['4. close'])

        if day1 > day2:
            print(1)
            return ((close2 - close1)/close1) * 100
        elif day2 > day1:
            print(2)
            return ((close1 - close2)/close2) * 100
            


if __name__ == '__main__':
    s = StockRequest()
    start_date = date(2023, 9, 24)
    end_date = date(2023, 9, 21)
    print(s.percent_diff_between_days('TSLA', start_date, end_date))
    