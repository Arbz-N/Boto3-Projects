EC2 Instance Management with Python Boto3

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


Project Structure
 
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


Configuration

    Before running, update the config section at the top of ec2_manager.py:
    
    pythonREGION        = "us-east-1"               # ← your region
    AMI_ID              = "ami-0c7217cdde317cfec"   # ← Ubuntu 22.04 AMI for your region
    INSTANCE_TYPE       = "t2.micro"
    KEY_NAME            = "your-key-pair"           # ← your key pair name
    SUBNET_ID           = "subnet-xxxxxxxxxx"       # ← your subnet ID
    
Architecture

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

