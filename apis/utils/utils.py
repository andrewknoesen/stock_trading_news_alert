import os
import json
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


script_dir = os.path.dirname(os.path.abspath(__file__))
stock_path = os.path.join(script_dir, '../../companies.json')


def get_stock_list() -> dict:
    logger.info(f"Stock path {stock_path}")

    with open(stock_path, 'r') as f:
        companies = json.load(f)

    return companies

def set_stock_list(companies:dict):
    logger.info(f"Setting stock list \n{companies}")

    with open(stock_path, 'w') as f:
        json.dump(companies, f, indent=4)