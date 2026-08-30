import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")

URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}


def get_columns(board_id):
    query = f"""
    query {{
        boards(ids: [{board_id}]) {{
            name
            columns {{
                id
                title
                type
            }}
        }}
    }}
    """

    response = requests.post(
        URL,
        json={"query": query},
        headers=HEADERS,
        timeout=30
    )

    result = response.json()

    if "errors" in result:
        print("ERROR:")
        print(result["errors"])
        return

    board = result["data"]["boards"][0]

    print("\nBOARD:", board["name"])
    print("-" * 60)

    for column in board["columns"]:
        print(
            f"{column['id']}  →  {column['title']}  ({column['type']})"
        )


print("DEALS COLUMNS")
get_columns(DEALS_BOARD_ID)

print("\n\nWORK ORDERS COLUMNS")
get_columns(WORK_ORDERS_BOARD_ID)