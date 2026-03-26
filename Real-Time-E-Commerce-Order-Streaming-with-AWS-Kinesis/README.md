# Real-Time E-Commerce Order Streaming with AWS Kinesis:

    Overview
    This project demonstrates real-time data streaming using AWS Kinesis Data Streams.
    A producer script generates 100 simulated e-commerce orders and publishes them to a Kinesis stream. 
    Consumer scripts read the records in real time from one or all shards.

    producer.py
        |
        | put_record() x 100
        v
    Kinesis Data Stream (Ecommerce-Orders-Stream)
        |-- Shard 0
        |-- Shard 1
        |
        | get_records()
        v
    consumer.py / multi-shard-consumer.py


## Project Structure:

    KinesisLab/
    |
    |-- products.py               # Product, city and payment data
    |-- producer.py               # Sends 100 orders to Kinesis
    |-- consumer.py               # Reads from a single shard
    |-- multi-shard-consumer.py   # Reads from all shards simultaneously
    |
    |-- README.md

## Prerequisites:

    python3 --version
    pip install boto3
    aws sts get-caller-identity


### Task 1 — Create Kinesis Stream:

    Console
    AWS Console → Kinesis → Create data stream
    
    Stream name:   Ecommerce-Orders-Stream
    Capacity mode: Provisioned
    Shards:        2
    
    Wait for status to become Active (~1 minute)


### Task 2 — Run the Producer:

    Update the CONFIG section in producer.py:
    pythonREGION = "your-region"
    python3 producer.py
    Expected output:
    =================================================================
    Sending 100 orders to Kinesis Stream...
    =================================================================
    [  1/100] ORD-0001 | Samsung Galaxy S26 Ultra      | Qty:2 | PKR  849,998 | Karachi
    [  2/100] ORD-0002 | MacBook Pro M4                | Qty:1 | PKR  599,999 | Lahore
    ...
    [100/100] ORD-0100 | iPad Pro M4 13-inch           | Qty:1 | PKR  299,999 | Peshawar
    
    [OK] All 100 orders sent to Kinesis!

### Task 3 — Run the Consumer:

    Get Shard IDs
    aws kinesis describe-stream \
      --stream-name Ecommerce-Orders-Stream \
      --region your-region \
      --query 'StreamDescription.Shards[*].ShardId'
    # ["shardId-000000000000", "shardId-000000000001"]

### Update the CONFIG section in consumer.py:

    REGION   = "your-region"
    SHARD_ID = "shardId-000000000000"

    Run Producer and Consumer Together
    
    # Terminal 1
    python3 producer.py
    
    # Terminal 2
    python3 consumer.py

    Consumer output:

    Consumer started — waiting for orders...
    ORD-0001 | Samsung Galaxy S26 Ultra      | Qty:2 | PKR  849,998 | Karachi    | JazzCash
    ORD-0002 | MacBook Pro M4                | Qty:1 | PKR  599,999 | Lahore     | Credit Card
    ORD-0003 | Sony WH-1000XM6               | Qty:3 | PKR  269,997 | Islamabad  | EasyPaisa


### Task 4 — Multi-Shard Consumer:
    
    Update the CONFIG in multi-shard-consumer.py:
    pythonREGION = "your-region"
    python3 multi-shard-consumer.py
    This consumer automatically discovers all shards and reads from each one in a round-robin loop.


### Key Concepts:

    PartitionKey and Shards
    pythonPartitionKey=order['category']
    Records with the same partition key always go to the same shard.
    Using category as the key means all Smartphone orders land on one shard, all Laptop orders on another, and so on. 
    This keeps related data together and makes shard-level analysis straightforward.

### Shard IteratorType:

    Type            Behavior
    LATEST          Read only new records from this point forward
    TRIM_HORIZON    Read all records from the beginning of the shard
    AT_TIMESTAMP    Read records from a specific timestamp

### Why Update NextShardIterator:

    Each get_records call returns a NextShardIterator token. 
    If you do not update the iterator before the next call, you will re-read the same records in an infinite loop.
    Shard Capacity
    Each shard supports 1 MB/sec write and 2 MB/sec read. With 2 shards the stream can handle 2 MB/sec inbound and 4 MB/sec outbound.

### Cleanup:

    # Delete the Kinesis stream to stop billing
    aws kinesis delete-stream \
      --stream-name Ecommerce-Orders-Stream \
      --region your-region
    
    # Verify deletion
    aws kinesis list-streams --region your-region
    
    # Remove local files
    rm -f producer.py consumer.py multi-shard-consumer.py products.py

