# consumer.py
# Kinesis stream se real-time orders receive karo

import boto3
import json
import time

region_name = 'us-east-1'
stream_name = 'Ecommerce-Orders-Stream'

kinesis_client = boto3.client('kinesis', region_name=region_name)

def consume_orders():
    # Step 1: ShardIterator nikalo — reading position set karo
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName=stream_name,
        # ShardId='shardId-000000000000',
        ShardId='shardId-000000000001',
        # ↑ Pehle shard se shuru karo
        # ↑ aws kinesis describe-stream se IDs dekho
        ShardIteratorType='LATEST'
        # ↑ LATEST = abhi se nayi records padho
        # ↑ Purani records ignore karo
    )['ShardIterator']
    # ↑ ['ShardIterator'] = response dict se token nikalo

    print("Consumer started — waiting for orders...")

    while True:
        # Step 2: Records padho
        records = kinesis_client.get_records(
            ShardIterator=shard_iterator,
            Limit=10
            # ↑ Ek baar mein max 10 records
        )

        # Step 3: Next position update karo
        shard_iterator = records['NextShardIterator']
        # ↑ ZAROORI — agar update nahi kiya to same records dobara milenge ❌

        # Step 4: Records process karo
        for record in records['Records']:
            order = json.loads(record['Data'])
            # ↑ JSON string → Python dict
            print(f" {order.get('order_id','N/A')} | "
                  f"{order.get('product_name','N/A')[:28]:<28} | "
                  f"Qty:{order.get('quantity','N/A')} | "
                  f"PKR {order.get('total_amount',0):>8,} | "
                  f"{order.get('city','N/A')} | "
                  f"{order.get('payment_method','N/A')}")

        time.sleep(2)
        # ↑ 2 sec wait karo — polling delay

consume_orders()