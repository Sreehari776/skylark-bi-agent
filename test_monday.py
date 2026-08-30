import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
url = "https://api.monday.com/v2"

headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

query = f"""
query {{
    boards(ids: [{BOARD_ID}]) {{
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
    url,
    json={"query": query},
    headers=headers
)

result = response.json()

print("Status:", response.status_code)

if "errors" in result:
    print("ERROR:")
    print(result["errors"])
else:
    board = result["data"]["boards"][0]

    print("Board:", board["name"])

    items = board["items_page"]["items"]

    print("Number of items:", len(items))

    print("\nFIRST 3 ITEMS:\n")

    for item in items[:3]:
        print("Item:", item["name"])

        for column in item["column_values"]:
            print(
                f"  {column['id']} = {column['text']}"
            )

        print()