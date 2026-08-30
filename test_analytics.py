from monday_client import get_deals, get_work_orders
from data_normalizer import normalize_deal, normalize_work_order
from analytics import (
    pipeline_summary,
    pipeline_by_sector,
    work_order_summary,
    work_orders_by_sector
)


# Get live data
_, raw_deals = get_deals()
_, raw_work_orders = get_work_orders()


# Clean data
deals = [
    normalize_deal(item)
    for item in raw_deals
]

work_orders = [
    normalize_work_order(item)
    for item in raw_work_orders
]


# Pipeline
print("\nPIPELINE SUMMARY")
print("================")

summary = pipeline_summary(deals)

for key, value in summary.items():
    print(f"{key}: {value}")


# Pipeline by sector
print("\nPIPELINE BY SECTOR")
print("==================")

sector_data = pipeline_by_sector(deals)

for sector, value in sorted(
    sector_data.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{sector}: {value}")


# Work orders
print("\nWORK ORDER SUMMARY")
print("==================")

wo_summary = work_order_summary(work_orders)

for key, value in wo_summary.items():
    print(f"{key}: {value}")


# Work orders by sector
print("\nWORK ORDERS BY SECTOR")
print("=====================")

wo_sector_data = work_orders_by_sector(work_orders)

for sector, value in sorted(
    wo_sector_data.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{sector}: {value}")