import boto3
import json
import time

kinesis_client = boto3.client('kinesis', region_name='us-east-1')
STREAM_NAME    = 'Ecommerce-Orders-Stream'

def get_all_shard_iterators():
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
    print(iterators)
    return iterators

def consume_all_shards():
    shard_iterators = get_all_shard_iterators()

    print("Consuming from all shards...")

    while True:
        for i, iterator in enumerate(shard_iterators):
            records = kinesis_client.get_records(
                ShardIterator=iterator, Limit=10
            )
            shard_iterators[i] = records['NextShardIterator']
            for record in records['Records']:
                order = json.loads(record['Data'])
                print(f"Shard {i} | {order['product_name']} | {order['customer_name']}")

        time.sleep(2)

consume_all_shards()