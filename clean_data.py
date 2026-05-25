import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA = BASE_DIR / "data" / "raw" / "orders.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "orders_clean.json"
REJECTED_DATA = BASE_DIR / "data" / "rejected" / "orders_rejected.json"


# filtred data
def clean_orders(orders):
    VALID_STATUSES = {"paid", "cancelled", "pending"}
    clean_data = []
    rejected_data = []
    seen_order_ids = set()

    for order in orders:
        # order_id
        try:
            order_id = int(order["order_id"])
        except (TypeError, ValueError):
            rejected_data.append({"raw": order, "error": "invalid order_id"})
            continue
        # duplicate check
        if order_id in seen_order_ids:
            rejected_data.append({"raw": order, "error": "duplicate order_id"})
            continue
        # customer_id check
        try:
            customer_id = int(order["customer_id"])
        except (TypeError, ValueError):
            rejected_data.append({"raw": order, "error": "invalid customer_id"})
            continue
        # status check
        try:
            status = order["status"].strip().lower()
        except AttributeError:
            rejected_data.append({"raw": order, "error": "invalid status"})
            continue

        if status not in VALID_STATUSES:
            rejected_data.append({"raw": order, "error": "invalid status"})
            continue

        # check amount
        try:
            amount = float(order["amount"])
        except (TypeError, ValueError):
            rejected_data.append({"raw": order, "error": "invalid amount"})
            continue

        if amount < 0:
            rejected_data.append({"raw": order, "error": "negative amount"})
            continue

        # check country
        country = order["country"]

        if not country:
            rejected_data.append({"raw": order, "error": "missing country"})
            continue

        # clean list
        clean_order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "status": status,
            "amount": amount,
            "country": country,
        }

        clean_data.append(clean_order)
        seen_order_ids.add(order_id)
    return clean_data, rejected_data


# Open CSV and import to list
def read_orders_from_csv(path):
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        orders = list(reader)
    print("check source")
    return orders


# Save result to JSON
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


order = read_orders_from_csv(RAW_DATA)
clean_data, rejected_data = clean_orders(order)

save_json(PROCESSED_DATA, clean_data)
save_json(REJECTED_DATA, rejected_data)


print(clean_orders(order))
print("Clean:", len(clean_data))
print("Reject:", len(rejected_data))
