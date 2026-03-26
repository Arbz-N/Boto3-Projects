import boto3
import json
import time

# ─────────────────────────────────────────────
# CONFIG — update these values before running
# ─────────────────────────────────────────────
REGION      = "your-region"              # e.g. us-east-1
STREAM_NAME = "Ecommerce-Orders-Stream"

kinesis_client = boto3.client('kinesis', region_name=REGION)


def get_all_shard_iterators():
    """Get shard iterators for every shard in the stream"""
    response = kinesis_client.describe_stream(StreamName=STREAM_NAME)
    shards   = response['StreamDescription']['Shards']

    iterators = []
    for shard in shards:
        iterator = kinesis_client.get_shard_iterator(
            StreamName=STREAM_NAME,
            ShardId=shard['ShardId'],
            ShardIteratorType='LATEST'
        )['ShardIterator']
        iterators.append(iterator)
        print(f"Iterator ready for: {shard['ShardId']}")

    return iterators


def consume_all_shards():
    shard_iterators = get_all_shard_iterators()
    print("Consuming from all shards...\n")

    while True:
        for i, iterator in enumerate(shard_iterators):
            response = kinesis_client.get_records(
                ShardIterator=iterator,
                Limit=10
            )

            # Update position for this shard
            shard_iterators[i] = response['NextShardIterator']

            for record in response['Records']:
                order = json.loads(record['Data'])
                print(f"Shard {i} | "
                      f"{order.get('order_id', 'N/A')} | "
                      f"{order.get('product_name', 'N/A')[:28]:<28} | "
                      f"{order.get('city', 'N/A')}")

        time.sleep(2)


consume_all_shards()