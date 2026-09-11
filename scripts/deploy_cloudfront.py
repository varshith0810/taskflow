import boto3
import json
import time

s3_client = boto3.client('s3', region_name='ap-south-1')
cf_client = boto3.client('cloudfront')
sts_client = boto3.client('sts')

bucket_name = "taskflow-frontend-prod-2k26"
region = "ap-south-1"
account_id = sts_client.get_caller_identity()['Account']

print(f"Connecting to AWS Account: {account_id}, Region: {region}")

# 1. Get or Create Origin Access Control (OAC)
oac_id = None
oacs = cf_client.list_origin_access_controls()
if 'OriginAccessControlList' in oacs and 'Items' in oacs['OriginAccessControlList']:
    for item in oacs['OriginAccessControlList']['Items']:
        if item['Name'] == 'taskflow-frontend-oac':
            oac_id = item['Id']
            print(f"Found existing OAC: {oac_id}")
            break

if not oac_id:
    print("Creating new Origin Access Control (OAC)...")
    res = cf_client.create_origin_access_control(
        OriginAccessControlConfig={
            'Name': 'taskflow-frontend-oac',
            'Description': 'OAC for TaskFlow S3 Frontend Bucket',
            'SigningProtocol': 'sigv4',
            'SigningBehavior': 'always',
            'OriginAccessControlOriginType': 's3'
        }
    )
    oac_id = res['OriginAccessControl']['Id']
    print(f"Created OAC: {oac_id}")

# 2. Check for existing Distribution pointing to this bucket
origin_domain = f"{bucket_name}.s3.{region}.amazonaws.com"
dist_id = None
dist_domain = None

dists = cf_client.list_distributions()
if 'DistributionList' in dists and 'Items' in dists['DistributionList']:
    for d in dists['DistributionList']['Items']:
        origins = d.get('Origins', {}).get('Items', [])
        for o in origins:
            if o.get('DomainName') == origin_domain:
                dist_id = d['Id']
                dist_domain = d['DomainName']
                print(f"Found existing distribution {dist_id} ({dist_domain})")
                break
        if dist_id:
            break

if not dist_id:
    print(f"Creating CloudFront Distribution for origin: {origin_domain}...")
    distribution_config = {
        'CallerReference': str(time.time()),
        'Comment': 'TaskFlow Frontend SPA Distribution',
        'Enabled': True,
        'DefaultRootObject': 'index.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': f'S3-{bucket_name}',
                    'DomainName': origin_domain,
                    'OriginAccessControlId': oac_id,
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': f'S3-{bucket_name}',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD']
                }
            },
            'Compress': True,
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,
            'MaxTTL': 31536000
        },
        'CustomErrorResponses': {
            'Quantity': 2,
            'Items': [
                {
                    'ErrorCode': 403,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 0
                },
                {
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 0
                }
            ]
        }
    }
    created = cf_client.create_distribution(DistributionConfig=distribution_config)
    dist_id = created['Distribution']['Id']
    dist_domain = created['Distribution']['DomainName']
    print(f"Successfully initiated CloudFront distribution creation!")
    print(f"Distribution ID: {dist_id}")
    print(f"CloudFront Domain: {dist_domain}")

# 3. Update S3 Bucket Policy to allow CloudFront OAC read
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/{dist_id}"
                }
            }
        }
    ]
}

print(f"Applying Bucket Policy to {bucket_name}...")
s3_client.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)
print("Bucket policy updated successfully!")

print(f"\nRESULT:")
print(f"CLOUDFRONT_DISTRIBUTION_ID={dist_id}")
print(f"CLOUDFRONT_DOMAIN_NAME={dist_domain}")
print(f"FRONTEND_URL=https://{dist_domain}")
