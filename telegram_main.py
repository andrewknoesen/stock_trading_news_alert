from apis.telegram import telegram_handler
    
def telegram_main():
    t = telegram_handler.Telegram()
    t.main()

if __name__ == '__main__':
    telegram_main()