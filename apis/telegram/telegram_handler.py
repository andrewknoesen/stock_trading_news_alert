import json
import logging
import os
import requests
from urllib.parse import urlencode
from pprint import pprint
from apis.utils import utils
from apis.news.news_request import NewsRequest
from enum import Enum, auto

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

reply_keyboard = [
    ["Get Current Stocks", "Update Stock list"],
    ["Get News"],
    ["Done"],
]

stock_modify_keyboard = [
    ["Remove stock"],
    ["Add stock"],
    ["Edit stock"]
]
stock_modify_markup = ReplyKeyboardMarkup(
    stock_modify_keyboard, one_time_keyboard=True)
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

class States(Enum):

    CHOOSING = auto()
    UPDATE_STOCKS = auto()
    DELETE_STOCK = auto()
    APPEND_STOCK = auto()
    EDIT_STOCK = auto()
    EDIT_STOCK_QUERY = auto()
    GET_NEWS = auto()

    ASK_CONFIRM = auto()
    REVIEW = auto()


class Telegram():

    def __init__(self) -> None:
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Combine the script directory with the 'key' file name
        key_path = os.path.join(self.script_dir, 'token')

        with open(key_path) as f:
            self.token = f.read()

        with open(os.path.join(self.script_dir, 'subscribers')) as f:
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

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask user for input."""
        await update.message.reply_text(
            "Greetings! \n"
            "What would you like to do?",
            reply_markup=markup,
        )

        return States.CHOOSING

    async def get_stocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the stock list an return it"""
        # stock_path = os.path.join(self.script_dir, '../../companies.json')
        # logger.info(f"Stock path {stock_path}")
        companies = dict({})
        try:
            # with open(stock_path, 'r') as f:
            #     companies = json.load(f)
            companies = utils.get_stock_list()

        except FileNotFoundError:
            await update.message.reply_text("The stock list file is not found.")
            return ConversationHandler.END

        await update.message.reply_text(
            "The current stock list is:"
        )

        # Convert the list of companies to a formatted string
        for k, v in companies.items():
            await update.message.reply_text(f'{k}: {v}')

        await update.message.reply_text(
            "What would you like to do?",
            reply_markup=markup,
        )

        return States.CHOOSING

    async def query_update_stocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Check how to modify stock list"""
        await update.message.reply_text(
            "How would you like to modify the stocks?",
            reply_markup=stock_modify_markup
        )

        return States.UPDATE_STOCKS

    async def update_stocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Modify stock list"""
        text = update.message.text

        match text:
            case "Remove stock":
                await update.message.reply_text(
                    "Which stock do you want to remove?",
                    reply_markup=ReplyKeyboardMarkup(
                        [list(utils.get_stock_list().keys())], one_time_keyboard=True)
                )

                return States.DELETE_STOCK
            case "Add stock":
                await update.message.reply_text(
                    "Please send stock in format TICKER:COMPANY_NAME"
                )

                return States.APPEND_STOCK
            case "Edit stock":
                await update.message.reply_text(
                    "Which stock do you want to edit?",
                    reply_markup=ReplyKeyboardMarkup(
                        [list(utils.get_stock_list().keys())], one_time_keyboard=True)
                )

                return States.EDIT_STOCK_QUERY
            case _:
                await update.message.reply_text(
                    "Invalid choice"
                )

                return ConversationHandler.END

    async def delete_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handler to remove a stock from the list of stocks"""
        try:
            companies = utils.get_stock_list()
            text = update.message.text
            companies.pop(text)
            utils.set_stock_list(companies)

            await update.message.reply_text(f"{text} removed.")

        except Exception as e:
            logger.error(e)
            await update.message.reply_text("The stock list file is not found.")

        finally:
            return ConversationHandler.END

    async def append_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handler to add a stock to the list of stocks"""
        try:
            companies = utils.get_stock_list()
            text = update.message.text

            if len(text.split(':')) != 2:
                await update.message.reply_text("Invalid format.")
                await update.message.reply_text(
                    "Please send stock in format TICKER:COMPANY_NAME"
                )

                return States.APPEND_STOCK

            new_company = text.split(':')
            companies[new_company[0]] = new_company[1]
            utils.set_stock_list(companies)

            await update.message.reply_text(f"{text} added.")

            return ConversationHandler.END

        except Exception as e:
            logger.error(e)
            await update.message.reply_text("The stock list file is not found.")

        finally:
            return ConversationHandler.END

    async def edit_stock_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Ask what to edit an existing stock with"""

        try:
            companies = utils.get_stock_list()
            text = update.message.text
            context.user_data["company"] = text


            await update.message.reply_text(
                f"{text} selected. What would you like to replace it with. \n"
                f"Current values is {companies[text]}."
            )

        except:
            await update.message.reply_text("The stock list file is not found.")

        finally:
            return States.EDIT_STOCK
        
    async def edit_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Edit existing stock"""

        try:
            companies = utils.get_stock_list()
            text = update.message.text
            companies[context.user_data["company"]] = text
            utils.set_stock_list(companies)

            await update.message.reply_text(
                f"New value for {context.user_data['company']} is {companies[context.user_data['company']]}."
            )

        except:
            await update.message.reply_text("The stock list file is not found.")

        finally:
            del context.user_data["company"]
            return ConversationHandler.END

    async def get_news_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Asking which stock to get news for"""
        await update.message.reply_text(
            "Please select a stock to get news for",
            reply_markup=ReplyKeyboardMarkup(
                        [list(utils.get_stock_list().keys())], one_time_keyboard=True)
        )

        return States.GET_NEWS
    
    async def get_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Return news articles"""
        news_handler = NewsRequest()
        text = update.message.text
        companies = utils.get_stock_list()
        articles = news_handler.get_article(company=companies[text])
        
        for article in articles:
            await update.message.reply_text(article)

        return ConversationHandler.END

    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Display the gathered info and end the conversation."""
        await update.message.reply_text(
            f"Cheers!",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    def main(self):

        # Create the bot and get the token from BotFather
        application = Application.builder().token(self.token).build()

        # Define the conversation handler
        # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                States.CHOOSING: [
                    MessageHandler(
                        filters.Regex("^Get Current Stocks$"), self.get_stocks
                    ),
                    MessageHandler(filters.Regex(
                        "^Update Stock list$"), self.query_update_stocks),
                    MessageHandler(filters.Regex("^Get News$"), self.get_news_request),
                ],
                States.UPDATE_STOCKS: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.update_stocks
                    )
                ],
                States.DELETE_STOCK: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.delete_stock
                    )
                ],
                States.APPEND_STOCK: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.append_stock
                    )
                ],
                States.EDIT_STOCK_QUERY: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.edit_stock_query
                    )
                ],
                States.EDIT_STOCK: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.edit_stock
                    )
                ],
                States.GET_NEWS: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(
                            "^Done$")), self.get_news
                    )
                ]
            },
            fallbacks=[MessageHandler(filters.Regex("^Done$"), self.done)],
        )

        application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    t = Telegram()
    # # print(t.get_updates())
    # print(t.send_message('test'))
    # while(True):
    #     print(t.get_updates)
    t.main()
