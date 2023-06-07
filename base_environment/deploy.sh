UUID_ENV=$(uuidgen)
UUID_ENV=${UUID_ENV:0:7}
UUID_ENV=$(echo $UUID_ENV | tr '[:upper:]' '[:lower:]')
BUCKET_NAME="cfn-base-environment-${UUID_ENV}"

aws s3 mb "s3://${BUCKET_NAME}"
aws cloudformation package --template-file base_environment/master.yaml --s3-bucket $BUCKET_NAME --output-template-file base_environment/master.template
aws cloudformation deploy --stack-name replication-base-environment --template-file base_environment/master.template --parameter-overrides file://base_environment/master_params.json --capabilities CAPABILITY_IAM
aws s3 rm "s3://${BUCKET_NAME}" --recursive
aws s3 rb "s3://${BUCKET_NAME}"