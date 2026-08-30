from monday_client import get_deals, get_work_orders


print("Getting Deals...")

deals_name, deals = get_deals()

print("Board:", deals_name)
print("Deals:", len(deals))


print("\nGetting Work Orders...")

wo_name, work_orders = get_work_orders()

print("Board:", wo_name)
print("Work Orders:", len(work_orders))