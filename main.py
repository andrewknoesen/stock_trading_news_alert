
from apis.stock_price import stock_request
from datetime import (
    date,
    timedelta,
)
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

def get_stock_diff():
    s = stock_request.StockRequest()
    return s.percent_diff_between_days(STOCK, date.today() - timedelta(days=1), date.today() - timedelta(days=2))

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
    ## STEP 1: Use https://www.alphavantage.co
    # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
    diff = get_stock_diff()
    if (abs(diff) >= 5):
        print("Get News")

    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    ## STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number. 

    
if __name__ == '__main__':
    main()