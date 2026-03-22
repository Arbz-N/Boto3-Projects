import boto3
import sys
import datetime
from botocore.exceptions import ClientError

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
REGION        = "us-east-1"
AMI_ID        = "ami-0c7217cdde317cfec"
INSTANCE_TYPE = "t2.micro"
KEY_NAME      = "your-key-pair"
SUBNET_ID     = "subnet-xxxxxxxxxx"


def create_instance(name):
    ec2 = boto3.resource("ec2", region_name=REGION)
    try:
        instances = ec2.create_instances(
            ImageId=AMI_ID,
            MinCount=1,
            MaxCount=1,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SubnetId=SUBNET_ID,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )
        iid = instances[0].id
        print(f"  Created: {iid} ({name})")
        return iid
    except ClientError as e:
        print(f"  Error: {e.response['Error']['Message']}")
        return None


def monitor_instance(instance_id):
    ec2_client   = boto3.client("ec2", region_name=REGION)
    ec2_resource = boto3.resource("ec2", region_name=REGION)

    print(f"  Waiting for running state...")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    instance = ec2_resource.Instance(instance_id)
    instance.reload()
    print(f"  Running! Public IP: {instance.public_ip_address}")
    return instance


def take_snapshot(instance_id):
    ec2_client = boto3.client("ec2", region_name=REGION)
    try:
        r = ec2_client.describe_instances(InstanceIds=[instance_id])
        vol = r['Reservations'][0]['Instances'][0] \
                ['BlockDeviceMappings'][0]['Ebs']['VolumeId']

        snap = ec2_client.create_snapshot(
            VolumeId=vol,
            Description=f"Snapshot {instance_id} {datetime.datetime.now()}"
        )
        print(f"  Snapshot created: {snap['SnapshotId']}")
        return snap['SnapshotId']
    except ClientError as e:
        print(f"  Error: {e.response['Error']['Message']}")
        return None


def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name=REGION)
    ec2_client.terminate_instances(InstanceIds=[instance_id])

    print(f"  Terminating...")
    waiter = ec2_client.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=[instance_id])
    print(f"  Terminated!")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  EC2 Manager — Boto3 Lab")
    print("=" * 50)

    # Step 1: Create
    print("\n[1] Creating instance...")
    iid = create_instance("boto3-lab-server")
    if not iid:
        sys.exit(1)

    # Step 2: Monitor
    print("\n[2] Monitoring state...")
    instance = monitor_instance(iid)

    # Step 3: Snapshot
    print("\n[3] Taking snapshot...")
    snap_id = take_snapshot(iid)

    # Step 4: Summary
    print("\n" + "=" * 50)
    print(f"  Instance ID : {iid}")
    print(f"  Snapshot ID : {snap_id}")
    if instance:
        print(f"  Public IP   : {instance.public_ip_address}")
    print("=" * 50)

    # Step 5: Cleanup
    print("\n[4] Terminating instance...")
    terminate_instance(iid)
    print("\n  Lab complete!")