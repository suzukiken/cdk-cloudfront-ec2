import json
import os
import boto3
import subprocess
import urllib.parse
import sys

cloudformation = boto3.resource("cloudformation")

output = subprocess.run(["cdk", "list"] + sys.argv[1:], capture_output=True)

stack_names = []
stacks = []

for line in output.stdout.decode("utf8").split("\n"):
    if line.strip():
        stack_names.append(line.strip())

print(stack_names)

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
            if "secretsmanager" in descr:
                if value.startswith("arn:aws:"):
                    name = "-".join(value.split(":")[6].split("-")[:-1])
                else:
                    name = value
                url = f"https://ap-northeast-1.console.aws.amazon.com/secretsmanager/secret?region=ap-northeast-1&name={name}"
            elif "s3" in descr:
                name = value
                url = f"https://s3.console.aws.amazon.com/s3/buckets/{name}?region=ap-northeast-1"
            elif "sns" in descr:
                if value.startswith("arn:aws:"):
                    name = value
                    url = f"https://ap-northeast-1.console.aws.amazon.com/sns/v3/home?region=ap-northeast-1#/topic/{name}"
            elif "sqs" in descr:
                if value.startswith("https:"):
                    name = urllib.parse.quote_plus(value)
                    url = f"https://ap-northeast-1.console.aws.amazon.com/sqs/v2/home?region=ap-northeast-1#/queues/{name}"
            elif "dynamodb" in descr:
                name = value
                url = f"https://ap-northeast-1.console.aws.amazon.com/dynamodbv2/home?region=ap-northeast-1#table?name={name}"
            elif "lambda" in descr:
                name = value
                url = f"https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/functions/{name}"
            elif "stepfunctions" in descr or "statemachine" in descr:
                if value.startswith("arn:aws:"):
                    name = value
                    url = f"https://ap-northeast-1.console.aws.amazon.com/states/home?region=ap-northeast-1#/statemachines/view/{name}"
            elif "cloudfront" in descr:
                name = value
                url = f"https://us-east-1.console.aws.amazon.com/cloudfront/v3/home?region=ap-northeast-1#/distributions/{name}"
            elif "iam" in descr:
                if value.startswith("arn:aws:"):
                    name = value.split("/")[1]
                    url = f"https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles/details/{name}"
            elif "appsync" in descr:
                if not value.startswith("https:"):
                    name = value
                    url = f"https://ap-northeast-1.console.aws.amazon.com/appsync/home?region=ap-northeast-1#/{name}/v1/home"
            elif "eventbridge" in descr:
                name = value
                url = f"https://ap-northeast-1.console.aws.amazon.com/events/home?region=ap-northeast-1#/eventbus/default/rules/{name}"
            if url:
                output.update({"URL": url})
        exported_values.append(output)

    stacks.append(
        {
            "Name": stack_name,
            "URL": f"https://ap-northeast-1.console.aws.amazon.com/cloudformation/home?region=ap-northeast-1#/stacks/stackinfo?stackId={stack.stack_id}",
            "Outputs": exported_values,
        }
    )

print(json.dumps(stacks, indent=4))
