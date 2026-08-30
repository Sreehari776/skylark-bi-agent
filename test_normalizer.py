from monday_client import get_deals, get_work_orders
from data_normalizer import normalize_deal, normalize_work_order


# Get live data from Monday
_, deals = get_deals()
_, work_orders = get_work_orders()


# Normalize the first item from each board
deal = normalize_deal(deals[0])
work_order = normalize_work_order(work_orders[0])


print("NORMALIZED DEAL")
print("----------------")
for key, value in deal.items():
    print(f"{key}: {value}")


print("\nNORMALIZED WORK ORDER")
print("----------------------")
for key, value in work_order.items():
    print(f"{key}: {value}")