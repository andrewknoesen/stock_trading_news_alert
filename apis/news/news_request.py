import os
from urllib.parse import urlencode
import requests
from datetime import date, timedelta

class NewsRequest:
    def __init__(self) -> None:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Combine the script directory with the 'key' file name
        key_path = os.path.join(script_dir, 'key')

        with open(key_path) as f:
            self.key = f.read()

        self.base_url = 'https://newsapi.org/v2/'

    def get_article(self, company, num_articles=3) -> list:
        data = {
            'q': company,
            'apiKey': self.key,
            'pageSize': num_articles,
            'language': 'en',
            'sortBy': 'popularity',
            'to': date.today(),
            'from': date.today() - timedelta(days=3)
        }

        params = urlencode(data)
        r = requests.get(url=f'{self.base_url}everything?', params=data)
        articles = r.json()['articles']

        response = []

        for article in articles:
            article_info = dict({})
            article_info['title'] = article['title']
            article_info['description'] = article['description']
            article_info['url'] = article['url']

            response.append(article_info)

        return response



if __name__ == '__main__':
    n = NewsRequest()
    print(n.get_article('Tesla'))