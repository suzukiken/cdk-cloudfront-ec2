
host=$(curl -X GET curl http://169.254.169.254/latest/meta-data/public-hostname)

sed -i -e 's/ec2-[-0-9]*.ap-northeast-1.compute.amazonaws.com/'"$host"'/' cdk.json

echo $host

cdk deploy