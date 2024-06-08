import boto3
import shutil
import uuid
import re
import time
import json

REGION = 'eu-north-1'

def create_iam_role(role_name, policy_document):
    iam_client = boto3.client('iam')
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            })
        )
        role_arn = response['Role']['Arn']
        print(f"IAM role created: {role_name}")
        # Attach policy to role
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=f"{role_name}Policy",
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Policy attached to role: {role_name}")
        return role_arn
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"IAM role already exists: {role_name}")
        # Retrieve existing role ARN
        role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
        # Update policy for the existing role
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=f"{role_name}Policy",
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Policy updated for role: {role_name}")
        return role_arn

def create_bucket(bucket_name, region):
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        print(f'S3 bucket created: {bucket_name}')
    except Exception as e:
        print(f'Failed to create bucket: {e}')
        raise

def generate_unique_bucket_name(prefix):
    bucket_name = f'{prefix}-{uuid.uuid4()}'
    bucket_name = bucket_name[:37]  # such as - 'parking-lot-lambda-functions-70bc833f'
    return bucket_name

def zip_lambda_function(source_dir, output_filename):
    shutil.make_archive(output_filename.replace('.zip', ''), 'zip', source_dir)

def upload_to_s3(file_name, bucket, object_name=None):
    s3_client = boto3.client('s3')
    if object_name is None:
        object_name = file_name
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f'Uploaded {file_name} to bucket {bucket} as {object_name}')
    except Exception as e:
        print(f'Failed to upload {file_name} to bucket {bucket}: {e}')
        raise

def deploy_cloudformation_stack(template_file, stack_name, bucket_name, entry_zip_key, exit_zip_key):
    cloudformation_client = boto3.client('cloudformation')
    with open(template_file, 'r') as file:
        template_body = file.read()
    try:
        response = cloudformation_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'BucketName',
                    'ParameterValue': bucket_name
                },
                {
                    'ParameterKey': 'EntryZipKey',
                    'ParameterValue': entry_zip_key
                },
                {
                    'ParameterKey': 'ExitZipKey',
                    'ParameterValue': exit_zip_key
                },
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        print('Stack creation initiated')
    except cloudformation_client.exceptions.AlreadyExistsException:
        response = cloudformation_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'BucketName',
                    'ParameterValue': bucket_name
                },
                {
                    'ParameterKey': 'EntryZipKey',
                    'ParameterValue': entry_zip_key
                },
                {
                    'ParameterKey': 'ExitZipKey',
                    'ParameterValue': exit_zip_key
                },
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        print('Stack update initiated')
    except Exception as e:
        print(f'Failed to create or update stack: {e}')
        raise
    return response

# Create IAM roles for Lambda functions
POLICY_DOCUMENT_ENTRY_FUNCTION = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "dynamodb:PutItem", "s3:GetObject"],
        "Resource": "*"
    }]
}

POLICY_DOCUMENT_EXIT_FUNCTION = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "dynamodb:GetItem", "dynamodb:UpdateItem", "s3:GetObject"],
        "Resource": "*"
    }]
}

ROLE_NAME_ENTRY_FUNCTION = 'EntryFunctionRole'
ROLE_NAME_EXIT_FUNCTION = 'ExitFunctionRole'

entry_role_arn = create_iam_role(ROLE_NAME_ENTRY_FUNCTION, POLICY_DOCUMENT_ENTRY_FUNCTION)
exit_role_arn = create_iam_role(ROLE_NAME_EXIT_FUNCTION, POLICY_DOCUMENT_EXIT_FUNCTION)

# Generate a unique bucket name
bucket_name = generate_unique_bucket_name('parking-lot-lambda-functions')

# Create S3 bucket if it doesn't exist
create_bucket(bucket_name, REGION)

# Zip Lambda function files
zip_lambda_function('entry_function', 'entry_function.zip')
zip_lambda_function('exit_function', 'exit_function.zip')

# Upload ZIP files to S3
upload_to_s3('entry_function.zip', bucket_name)
upload_to_s3('exit_function.zip', bucket_name)

# Deploy CloudFormation stack
deploy_cloudformation_stack('template.yaml', 'ParkingLotStack', bucket_name, 'entry_function.zip', 'exit_function.zip')
print('Deployment complete')
