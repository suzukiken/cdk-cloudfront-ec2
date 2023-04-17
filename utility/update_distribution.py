import json
import os
import boto3
import requests
import subprocess
import sys
import datetime

cloudformation = boto3.resource("cloudformation")
cloudfront = boto3.client('cloudfront')

output = subprocess.run(["cdk", "list"] + sys.argv[1:], capture_output=True)

stack_names = []
distribution_url = None
distribution_id = None

for line in output.stdout.decode("utf8").split("\n"):
    if line.strip():
        stack_names.append(line.strip())

for stack_name in stack_names:
    stack = cloudformation.Stack(stack_name)
    exported_values = []

    try:
        outputs = stack.outputs
    except:
        pass

    if not outputs:
        outputs = []

    for output in outputs:
        if output.get("Description"):
            descr = output.get("Description").lower()
            value = output.get("OutputValue")
            url = ""
            if "cloudfront" in descr:
                distribution_id = value
                distribution_url = f"https://us-east-1.console.aws.amazon.com/cloudfront/v3/home?region=ap-northeast-1#/distributions/{distribution_id}"

r = requests.get('http://169.254.169.254/latest/meta-data/public-hostname/')
cloud9_host = r.text

distribution_config_response = cloudfront.get_distribution_config(Id=distribution_id)

distribution_etag = distribution_config_response['ETag']

distribution_config = distribution_config_response['DistributionConfig']
distribution_config['Comment'] = datetime.datetime.now().isoformat()
distribution_config['Origins']['Items'][0]['DomainName'] = cloud9_host
        
response = cloudfront.update_distribution(
    Id=distribution_id,
    IfMatch=distribution_etag,
    DistributionConfig=distribution_config
)

print(distribution_url)

    
