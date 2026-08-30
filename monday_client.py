import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")

MONDAY_URL = "https://api.monday.com/v2"


def get_board_items(board_id):
    """Get all items from a Monday.com board."""

    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }

    query = f"""
    query {{
        boards(ids: [{board_id}]) {{
            name
            items_page(limit: 500) {{
                cursor
                items {{
                    id
                    name
                    column_values {{
                        id
                        text
                        value
                    }}
                }}
            }}
        }}
    }}
    """

    response = requests.post(
        MONDAY_URL,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise Exception(result["errors"])

    board = result["data"]["boards"][0]

    return board["name"], board["items_page"]["items"]


def get_deals():
    """Get all Deals."""
    return get_board_items(DEALS_BOARD_ID)


def get_work_orders():
    """Get all Work Orders."""
    return get_board_items(WORK_ORDERS_BOARD_ID)