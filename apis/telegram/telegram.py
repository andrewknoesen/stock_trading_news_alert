import os
import requests
from urllib.parse import urlencode
from pprint import pprint

class Telegram():
    def __init__(self) -> None:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Combine the script directory with the 'key' file name
        key_path = os.path.join(script_dir, 'token')

        with open(key_path) as f:
            self.token = f.read()

        with open(os.path.join(script_dir, 'subscribers')) as f:
            self.subscriber = f.read()

        self.base_url = f'https://api.telegram.org/bot{self.token}/'

    def send_message(self, message):

        data = {
            'chat_id': self.subscriber,
            'text': message,
            'parse_mode': 'markdown'
        }

        pprint(data)

        params = urlencode(data)
        r = requests.get(url=f'{self.base_url}sendMessage', params=data)
        return r.json()
    
    def get_chat(self):
        r = requests.get(url=f'{self.base_url}getChat')
        return r.json()
    
    def get_updates(self):
        r = requests.get(url=f'{self.base_url}getUpdates')
        return r.json()


if __name__ == '__main__':
    t = Telegram()
    # print(t.get_updates())
    print(t.send_message('test'))