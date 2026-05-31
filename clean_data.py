import csv
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA = BASE_DIR / "data" / "raw" / "orders.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "orders_clean.json"
REJECTED_DATA = BASE_DIR / "data" / "rejected" / "orders_rejected.json"
PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)
REJECTED_DATA.parent.mkdir(parents=True, exist_ok=True)


# fuction for parse date
def parse_datetime(date):
    try:
        parsed_date = datetime.fromisoformat(date)
    except (TypeError, ValueError):
        return None
    return parsed_date


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

        # try:
        #     order_date = datetime.fromisoformat(order["order_date"])
        # except:
        #     rejected_data.append({"raw": order, "error": "invalid date"})
        #     continue
        # try:
        #     updated_at = datetime.fromisoformat(order["updated_at"])
        # except:
        #     rejected_data.append({"raw": order, "error": "invalid date"})
        #     continue

        # check country
        country = order["country"]

        if not country:
            rejected_data.append({"raw": order, "error": "missing country"})
            continue

        order_date = parse_datetime(order["order_date"])
        updated_at = parse_datetime(order["updated_at"])

        if order_date == None or updated_at == None:
            rejected_data.append({"raw": order, "error": "invalid date"})
            continue

        # clean list
        clean_order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "status": status,
            "amount": amount,
            "country": country,
            "order_date": order_date.isoformat(),
            "updated_at": updated_at.isoformat(),
        }

        clean_data.append(clean_order)
        seen_order_ids.add(order_id)
    return clean_data, rejected_data


# Open CSV and import to list
def read_orders_from_csv(path):
    logging.info("Reading orders from: s%", path)

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        orders = list(reader)
    logging.info("Orders loaded from CSV: %s", len(orders))
    return orders


# Save result to JSON
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    order = read_orders_from_csv(RAW_DATA)

    clean_data, rejected_data = clean_orders(order)

    save_json(PROCESSED_DATA, clean_data)
    save_json(REJECTED_DATA, rejected_data)

    logging.info("Raw rows loaded: %s", len(order))
    logging.info("Clean rows saved: %s", len(clean_data))
    logging.info("Rejected rows saved: %s", len(rejected_data))
    logging.info("Clean data path: %s", PROCESSED_DATA)
    logging.info("Rejected data path: %s", REJECTED_DATA)


if __name__ == "__main__":
    main()
