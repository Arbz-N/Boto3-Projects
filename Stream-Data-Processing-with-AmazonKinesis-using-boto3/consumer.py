import boto3
import json
import time

region_name = 'us-east-1'
stream_name = 'Ecommerce-Orders-Stream'

kinesis_client = boto3.client('kinesis', region_name=region_name)

def consume_orders():
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName=stream_name,
        ShardId='shardId-000000000001',
        ShardIteratorType='LATEST'
    )['ShardIterator']

    print("Consumer started — waiting for orders...")

    while True:
        records = kinesis_client.get_records(
            ShardIterator=shard_iterator,
            Limit=10
        )

        shard_iterator = records['NextShardIterator']

        for record in records['Records']:
            order = json.loads(record['Data'])
            print(f" {order.get('order_id','N/A')} | "
                  f"{order.get('product_name','N/A')[:28]:<28} | "
                  f"Qty:{order.get('quantity','N/A')} | "
                  f"PKR {order.get('total_amount',0):>8,} | "
                  f"{order.get('city','N/A')} | "
                  f"{order.get('payment_method','N/A')}")

        time.sleep(2)
        # ↑ 2 sec wait  — polling delay

consume_orders()