from monday_client import get_deals
from data_normalizer import normalize_deal


_, raw_deals = get_deals()

deals = [
    normalize_deal(item)
    for item in raw_deals
]

print("\nACTIVE MINING DEALS")
print("===================")

count = 0

for deal in deals:

    status = (deal.get("deal_status") or "").lower()
    sector = (deal.get("sector") or "").lower()

    if sector == "mining" and status in ["open", "on hold"]:

        count += 1

        print("\nDeal:", deal["deal_name"])
        print("Status:", deal["deal_status"])
        print("Value:", deal["deal_value"])
        print("Tentative Close:", deal["tentative_close_date"])
        print("Actual Close:", deal["actual_close_date"])
        print("Stage:", deal["deal_stage"])

print("\nTotal active Mining deals:", count)