import json
import os
import boto3
import requests
import subprocess
import sys

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


distribution_response = cloudfront.get_distribution(
    Id=distribution_id
)

current_domain = distribution_response["Distribution"]["DistributionConfig"]["Origins"]["Items"][0]["DomainName"]

r = requests.get('http://169.254.169.254/latest/meta-data/public-hostname/')
cloud9_host = r.text

r = requests.get('http://169.254.169.254/latest/meta-data/security-groups/')
security_group_name = r.text

security_group_url = f"https://ap-northeast-1.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-1#SecurityGroups:group-name={security_group_name}"

print(f"CloudFront Distribution: {distribution_url}")
print(f"Security Group (need to set 8080 access from 0.0.0.0): {security_group_url}")

if cloud9_host != current_domain:
    print(f"Cloud9 Host Name: {cloud9_host}")
else:
    print("no need to setup")





