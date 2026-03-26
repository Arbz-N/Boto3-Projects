import boto3
import json
import time

# ─────────────────────────────────────────────
# CONFIG — update these values before running
# ─────────────────────────────────────────────
REGION      = "your-region"              # e.g. us-east-1
STREAM_NAME = "Ecommerce-Orders-Stream"
SHARD_ID    = "shardId-000000000000"     # get shard IDs from describe-stream

kinesis_client = boto3.client('kinesis', region_name=REGION)


def consume_orders():
    # Get a shard iterator — sets the starting read position
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=SHARD_ID,
        ShardIteratorType='LATEST'   # read only new records from this point
    )['ShardIterator']

    print("Consumer started — waiting for orders...")

    while True:
        # Read a batch of records
        response = kinesis_client.get_records(
            ShardIterator=shard_iterator,
            Limit=10   # max records per call
        )

        # Update iterator to the next position — required to avoid re-reading records
        shard_iterator = response['NextShardIterator']

        # Process each record
        for record in response['Records']:
            order = json.loads(record['Data'])   # JSON string → Python dict
            print(f"{order.get('order_id', 'N/A')} | "
                  f"{order.get('product_name', 'N/A')[:28]:<28} | "
                  f"Qty:{order.get('quantity', 'N/A')} | "
                  f"PKR {order.get('total_amount', 0):>8,} | "
                  f"{order.get('city', 'N/A')} | "
                  f"{order.get('payment_method', 'N/A')}")

        time.sleep(2)   # polling interval in seconds


consume_orders()