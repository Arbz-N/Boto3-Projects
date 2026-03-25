
import boto3
import json
import random
import time
from products import PRODUCTS, CITIES, PAYMENT_METHODS

kinesis = boto3.client('kinesis', region_name='us-east-1')

def generate_order(order_id):
    """Realistic e-commerce order generate karo"""
    product  = random.choice(PRODUCTS)
    quantity = random.randint(1, 3)

    return {
        "order_id":       f"ORD-{order_id:04d}",
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

# ─────────────────────────────────────────
# 100 ORDERS KINESIS MEIN BHEJO
# ─────────────────────────────────────────
print("=" * 65)
print("Sending 100 orders to Kinesis Stream...")
print("=" * 65)

for i in range(1, 101):
    order = generate_order(i)

    response = kinesis.put_record(
        StreamName='Ecommerce-Orders-Stream',
        Data=json.dumps(order),
        PartitionKey=order['category']
    )

    print(f"[{i:3d}/100] {order['order_id']} | "
          f"{order['product_name'][:28]:<28} | "
          f"Qty:{order['quantity']} | "
          f"PKR {order['total_amount']:>8,} | "
          f"{order['city']}")

    time.sleep(0.5)
    # ↑ 0.5 sec delay — rate limiting

print(" All 100 orders sent to Kinesis!")