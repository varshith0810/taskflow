import boto3
import time

ec2 = boto3.client('ec2', region_name='ap-south-1')

AMI_ID = "ami-0c0fd09cfe77b59dc"  # Ubuntu 24.04 LTS (Noble)
INSTANCE_TYPE = "t3.micro"
KEY_NAME = "taskflow-key"
SUBNET_ID = "subnet-0faa7d8539d3ff564"  # Public subnet in ap-south-1b (Same AZ as RDS!)
SECURITY_GROUPS = ["sg-030002c481518dbd9", "sg-0af340a9a52a8461b"]  # taskflow-ec2-sg & rds access
ELASTIC_IP_ALLOC_ID = "eipalloc-0e39f77e1de46dc2e"  # 13.234.146.200

user_data_script = """#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "[1/7] Updating package index..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-pip python3-venv git curl iptables

echo "[2/7] Setting up swap space (1GB)..."
fallocate -l 1G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=1024
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

echo "[3/7] Cloning repository..."
mkdir -p /app
cd /app
git clone https://github.com/varshith0810/TaskFlow.git .

echo "[4/7] Writing production environment configuration..."
cat << 'ENV' > /app/backend/.env
APP_NAME=TaskFlow
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
PORT=80
HOST=0.0.0.0
DATABASE_URL=postgresql://taskflow_admin:taskflow_secure_password_123@taskflow-postgres.cneiwugmcqwx.ap-south-1.rds.amazonaws.com:5432/taskflow_db
SECRET_KEY=prod-taskflow-ultra-secure-random-key-64bytes-2026
ALLOWED_ORIGINS=http://taskflow-frontend-prod-2k26.s3-website.ap-south-1.amazonaws.com,http://localhost:5173,http://13.234.146.200,http://localhost:3000
ENV

echo "[5/7] Setting up Python virtual environment..."
python3 -m venv /app/.venv
/app/.venv/bin/pip install --upgrade pip
/app/.venv/bin/pip install -r /app/backend/requirements.txt uvicorn psycopg2-binary httpx

echo "[6/7] Waiting for RDS PostgreSQL database to accept connections and running seeds..."
cd /app/backend
for i in $(seq 1 40); do
  if /app/.venv/bin/python -c "from app.db.session import engine; engine.connect(); print('Connected to PostgreSQL successfully!')" 2>/dev/null; then
    echo "Database ready! Running initial seed..."
    /app/.venv/bin/python seed.py || true
    break
  fi
  echo "Database not ready yet (attempt $i/40), waiting 5 seconds..."
  sleep 5
done

echo "[7/7] Configuring systemd service for TaskFlow API..."
cat << 'SERVICE' > /etc/systemd/system/taskflow.service
[Unit]
Description=TaskFlow FastAPI Production Server
After=network.target

[Service]
User=root
WorkingDirectory=/app/backend
EnvironmentFile=/app/backend/.env
ExecStart=/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable taskflow
systemctl start taskflow

# Forward port 8000 to port 80 so requests on either port work
iptables -t nat -A PREROUTING -p tcp --dport 8000 -j REDIRECT --to-port 80 || true

echo "=== TaskFlow API deployment completed successfully! ==="
"""

print("Launching new EC2 backend instance in ap-south-1b...")
res = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_NAME,
    SubnetId=SUBNET_ID,
    SecurityGroupIds=SECURITY_GROUPS,
    UserData=user_data_script,
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'taskflow-server'}]
        }
    ]
)
instance_id = res['Instances'][0]['InstanceId']
print(f"Launched instance: {instance_id}")

print("Waiting for instance to be in 'running' state...")
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])
print("Instance is now running!")

print(f"Associating Elastic IP ({ELASTIC_IP_ALLOC_ID} -> 13.234.146.200)...")
ec2.associate_address(
    AllocationId=ELASTIC_IP_ALLOC_ID,
    InstanceId=instance_id,
    AllowReassociation=True
)
print("Elastic IP 13.234.146.200 successfully associated!")
