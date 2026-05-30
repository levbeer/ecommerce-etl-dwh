import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent

CLEAN_DATA = BASE_DIR / "data" / "processed" / "orders_clean.json"
METRICS_DATA = BASE_DIR / "data" / "processed" / "orders_metrics.json"


def read_json(path):
    logging.info("Reading JSON from: %s", path)

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def save_json(path, data):
    logging.info("Saving JSON to: %s", path)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    logging.info("JSON saved successfully")


def calculate_metrics(orders):
    total_order = len(orders)
    total_revenue = 0
    revenue_by_country = {}
    orders_by_status = {}
    for order in orders:
        status = order["status"]
        orders_by_status[status] = orders_by_status.get(status, 0) + 1

        if status == "paid":
            amount = order["amount"]
            country = order["country"]

            total_revenue += amount
            revenue_by_country[country] = revenue_by_country.get(country, 0) + amount

    paid_orders = orders_by_status.get("paid", 0)
    cancelled_orders = orders_by_status.get("cancelled", 0)
    pending_orders = orders_by_status.get("pending", 0)
    average_order_value = total_revenue / paid_orders if paid_orders > 0 else 0

    return {
        "total_orders": total_order,
        "paid_orders": paid_orders,
        "cancelled_orders": cancelled_orders,
        "pending_orders": pending_orders,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(average_order_value, 2),
        "revenue_by_country": revenue_by_country,
        "orders_by_status": orders_by_status,
    }


orders = read_json(CLEAN_DATA)

metrics = calculate_metrics(orders)

save_json(METRICS_DATA, metrics)

logging.info("Metrics calculated: %s", metrics)
