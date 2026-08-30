from monday_client import get_deals, get_work_orders
from data_normalizer import normalize_deal, normalize_work_order


_, raw_deals = get_deals()
_, raw_work_orders = get_work_orders()

deals = [normalize_deal(x) for x in raw_deals]
work_orders = [normalize_work_order(x) for x in raw_work_orders]


print("\nDEAL STATUSES")
print("=============")

deal_statuses = set()

for deal in deals:
    deal_statuses.add(deal.get("deal_status"))

for status in sorted(deal_statuses, key=str):
    print(repr(status))


print("\nWORK ORDER EXECUTION STATUSES")
print("=============================")

wo_statuses = set()

for wo in work_orders:
    wo_statuses.add(wo.get("execution_status"))

for status in sorted(wo_statuses, key=str):
    print(repr(status))


print("\nSECTORS")
print("=======")

sectors = set()

for deal in deals:
    sectors.add(deal.get("sector"))

for sector in sorted(sectors, key=str):
    print(repr(sector))