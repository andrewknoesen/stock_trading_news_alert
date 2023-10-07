
from apis.stock_price import stock_request
from apis.news import news_request
from apis.telegram import telegram_handler
from datetime import (
    date,
    timedelta,
)
from time import sleep

import json

# COMPANIES = {
#     'TSLA': "Tesla",
#     'GOOGL': 'Google',
#     'AAPL': 'Apple',
#     'NVDA': 'Nvidia',
# }

COMPANIES = {}

MSG = """
$ticker

*$title*

$link
            
$summary
"""

def get_stock_diff(stock):
    s = stock_request.StockRequest()
    return s.percent_diff_between_days(stock, date.today() - timedelta(days=1), date.today() - timedelta(days=2))

def get_article(company):
    n = news_request.NewsRequest()
    return n.get_article(company)

def send_message(message):
    t = telegram_handler.Telegram()
    return t.send_message(message)

def load_companies():
    with open("./companies.json") as f:
        c = json.load(f)

    return c


def export_companies(companies):
    with open("./companies1.json", "w") as f:
        json.dump(companies, f, indent=4)
#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

def main():
    companies = load_companies()
    
    for k,v in companies.items():
        articles = None
        ## STEP 1: Use https://www.alphavantage.co
        # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
        diff = get_stock_diff(k)
        if 'no entries' == diff:
            sleep(12) #for fair use in api
            continue

        ## STEP 2: Use https://newsapi.org
        # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
        if (abs(diff) >= 5):
            articles = get_article(v)

        ## STEP 3: Use https://www.twilio.com
        # Send a seperate message with the percentage change and each article's title and description to your phone number. 
        if articles is not None and(len(articles) > 0):
            for article in articles:
                msg=MSG
                if diff > 0:
                    diff_msg = f'🔺{int(diff)}%'
                else:
                    diff_msg = f'🔻{int(diff)}%'

                msg = msg.replace('$ticker', f'{k}: {diff_msg}')
                msg = msg.replace('$title', article["title"])
                msg = msg.replace('$link', article["url"])
                msg = msg.replace('$summary', article["description"])
                send_message(str(msg))

if __name__ == '__main__':
    main()