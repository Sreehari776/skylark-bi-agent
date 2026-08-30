from monday_client import get_work_orders
from data_normalizer import normalize_work_order
from analytics import customer_risk_analysis


board, work_orders = get_work_orders()

normalized_work_orders = [
    normalize_work_order(wo)
    for wo in work_orders
]

risks = customer_risk_analysis(normalized_work_orders)

print("\nTOP CUSTOMER RISKS")
print("==================")

for customer, data in risks[:10]:

    print(
        customer,
        "→ Receivable:",
        data["receivable"],
        "| Risk Score:",
        data["risk_score"],
        "| Billing Issues:",
        data["billing_issues"],
        "| Operational Issues:",
        data["operational_issues"]
    )