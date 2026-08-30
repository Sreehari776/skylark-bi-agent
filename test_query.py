from monday_client import get_deals
from data_normalizer import normalize_deal
from query_engine import pipeline_query


# Get live Deals
_, raw_deals = get_deals()

# Normalize
deals = [
    normalize_deal(item)
    for item in raw_deals
]


# Example founder question:
# Mining pipeline for Q1 2026

result = pipeline_query(
    deals,
    sector="Mining",
    quarter="Q1",
    year=2026
)


print("\nFOUNDER QUERY")
print("=============")

print("Sector: Mining")
print("Quarter: Q1 2026")

print(
    "Number of deals:",
    result["number_of_deals"]
)

print(
    "Pipeline value:",
    result["pipeline_value"]
)