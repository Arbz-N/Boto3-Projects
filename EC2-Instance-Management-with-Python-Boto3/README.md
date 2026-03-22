# EC2 Instance Management with Python Boto3

    Overview
    This is a hands-on project that demonstrates full EC2 lifecycle management using Boto3 — 
    the official AWS SDK for Python. A single script handles instance creation, state monitoring via waiters, 
    EBS snapshot creation, and termination with cleanup.
    Key highlights:
    
    boto3.resource used for instance creation and attribute access
    boto3.client used for waiters, snapshots, and termination
    Waiters used for state transitions: instance_running and instance_terminated
    EBS snapshot created from the root volume while instance is running
    ClientError exception handling on every AWS operation
    Full lifecycle in one script: create → wait → snapshot → terminate


## Project Structure:
 
    EC2-Instance-Management-with-Python-Boto3/
    │
    ├── ec2_manager.py      # Main script — EC2 full lifecycle
    ├── requirements.txt    # boto3 dependency
    │
    └── README.md

##  Prerequisites:

    Requirement            Check 

    Python3.8+             python3 --version 
    pip                    pip3 --version
    AWS CLI                aws --version
    AWS credentials        aws sts get-caller-identity
    Key pair               Existing EC2 key pair in your region
    Subnet ID              Any subnet in your VPC


## Configuration:

    Before running, update the config section at the top of ec2_manager.py:
    
    pythonREGION        = "us-east-1"               # ← your region
    AMI_ID              = "ami-0c7217cdde317cfec"   # ← Ubuntu 22.04 AMI for your region
    INSTANCE_TYPE       = "t2.micro"
    KEY_NAME            = "your-key-pair"           # ← your key pair name
    SUBNET_ID           = "subnet-xxxxxxxxxx"       # ← your subnet ID
    
## Architecture:

        ec2_manager.py
          │
          ├── create_instance()
          │     boto3.resource.create_instances()
          │     → EC2 instance (t2.micro, Ubuntu 22.04)
          │     → Tag: Name=boto3-lab-server
          │
          ├── monitor_instance()
          │     waiter: instance_running
          │     → instance.public_ip_address
          │
          ├── take_snapshot()
          │     describe_instances → root VolumeId
          │     create_snapshot(VolumeId)
          │     → snap-xxxxxxxxxxxxxxxxx
          │
          └── terminate_instance()
                terminate_instances()
                waiter: instance_terminated
                → instance gone 

  boto3.resource  → create_instances(), Instance()
  boto3.client    → waiters, snapshots, terminate


## Setup

### Create and activate virtual environment:
    
    python3 -m venv boto3-lab
    source boto3-lab/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    pip list | grep boto3  # boto3  1.xx.x 


### Update Config in ec2_manager.py:

    REGION        = "us-east-1"         # your region
    AMI_ID        = "ami-0b6c6ebed2801a5cb"  # Ubuntu 22.04
    INSTANCE_TYPE = "t2.micro"
    KEY_NAME      = "your-key-pair"     # your key pair name
    SUBNET_ID     = "subnet-xxxxxxxx"   # your subnet ID

### Run:

    python3 ec2_manager.py

### Expected Output:

    ==================================================
      EC2 Manager — Boto3 Lab
    ==================================================
    
    [1] Creating instance...
      Created: i-0abc1234567890def (boto3-lab-server)
    
    [2] Monitoring state...
      Waiting for running state...
      Running! Public IP: 54.x.x.x
    
    [3] Taking snapshot...
      Snapshot created: snap-0abc1234567890def
    
    ==================================================
      Instance ID : i-0abc1234567890def
      Snapshot ID : snap-0abc1234567890def
      Public IP   : 54.x.x.x
    ==================================================
    
    [4] Terminating instance...
      Terminating...
      Terminated!
    
    [5] Deleting snapshot...
      Waiting for snapshot to complete...
      Snapshot completed!
      Snapshot deleted: snap-0abc1234567890def
    
    ==================================================
      Lab complete! 
    ==================================================

### Cleanup:

    Deactivate venv
    deactivate
    rm -rf boto3-lab/
    
    # If instance still running (script interrupted):
    aws ec2 describe-instances \
      --filters "Name=tag:Name,Values=boto3-lab-server" \
                "Name=instance-state-name,Values=running" \
      --query 'Reservations[*].Instances[*].InstanceId' \
      --output text
    
    aws ec2 terminate-instances --instance-ids i-xxxxxxxxxxxxxxxxx
    
    # If snapshot still exists:
    aws ec2 describe-snapshots \
      --filters "Name=description,Values=Snapshot*boto3*" \
      --query 'Snapshots[*].SnapshotId' --output text
    
    aws ec2 delete-snapshot --snapshot-id snap-xxxxxxxxxxxxxxxxx
    
### License:

    This project is licensed under the MIT License.