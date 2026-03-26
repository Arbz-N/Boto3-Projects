import boto3
import json
import random
import time

from products import PRODUCTS, CITIES, PAYMENT_METHODS
# products.py must be in the same directory

# ─────────────────────────────────────────────
# CONFIG — update these values before running
# ─────────────────────────────────────────────
REGION      = "your-region"              # e.g. us-east-1
STREAM_NAME = "Ecommerce-Orders-Stream"

kinesis = boto3.client('kinesis', region_name=REGION)


def generate_order(order_id):
    """Generate a realistic e-commerce order"""
    product  = random.choice(PRODUCTS)
    quantity = random.randint(1, 3)

    return {
        "order_id":       f"ORD-{order_id:04d}",   # ORD-0001, ORD-0042 etc.
        "product_name":   product["name"],
        "category":       product["category"],
        "unit_price":     product["price"],
        "quantity":       quantity,
        "total_amount":   product["price"] * quantity,
        "customer_name":  f"Customer-{random.randint(1, 1000):04d}",
        "city":           random.choice(CITIES),
        "payment_method": random.choice(PAYMENT_METHODS),
        "status":         "PENDING"
    }


# ─────────────────────────────────────────────
# Send 100 orders to the Kinesis stream
# ─────────────────────────────────────────────
print("=" * 65)
print("Sending 100 orders to Kinesis Stream...")
print("=" * 65)

for i in range(1, 101):
    order = generate_order(i)

    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(order),          # dict must be serialized to string
        PartitionKey=order['category']   # same category routes to the same shard
    )

    print(f"[{i:3d}/100] {order['order_id']} | "
          f"{order['product_name'][:28]:<28} | "
          f"Qty:{order['quantity']} | "
          f"PKR {order['total_amount']:>8,} | "
          f"{order['city']}")

    time.sleep(0.5)   # small delay to avoid hitting rate limits

print("\n[OK] All 100 orders sent to Kinesis!")