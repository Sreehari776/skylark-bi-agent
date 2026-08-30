import sys
from analytics import load_data, data_quality_summary, format_data_quality_warning

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

deals, work_orders = load_data()
quality = data_quality_summary(deals, work_orders)

print("DATA QUALITY SUMMARY:")
print(quality)

print("\nFORMATTED WARNING:")
print(format_data_quality_warning(quality))