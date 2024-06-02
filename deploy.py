import boto3
import shutil
import uuid
import re

# Constants
ENTRY_FUNCTION_NAME = 'entry_handler'
EXIT_FUNCTION_NAME = 'exit_handler'
ENTRY_ZIP = 'entry_handler.zip'
EXIT_ZIP = 'exit_handler.zip'
TEMPLATE_FILE = 'template.yaml'
STACK_NAME = 'ParkingLotStack'

def create_bucket(bucket_name, region):
    s3_client = boto3.client('s3', region_name=region)
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

def generate_valid_bucket_name():
    # Generate a unique bucket name
    bucket_name = f'parking-lot-lambda-functions-bucket-{str(uuid.uuid4())}'
    # Remove invalid characters
    bucket_name = re.sub(r'[^a-zA-Z0-9.-]', '', bucket_name)
    # Ensure bucket name length is within the limits
    bucket_name = bucket_name[:63]
    return bucket_name

def zip_lambda_function(source_dir, output_filename):
    shutil.make_archive(output_filename.replace('.zip', ''), 'zip', source_dir)

def upload_to_s3(file_name, bucket, object_name=None):
    s3_client = boto3.client('s3')
    if object_name is None:
        object_name = file_name
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response

def deploy_cloudformation_stack(template_file, stack_name):
    cloudformation_client = boto3.client('cloudformation')
    with open(template_file, 'r') as file:
        template_body = file.read()
    try:
        response = cloudformation_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        print('Stack creation initiated.')
    except cloudformation_client.exceptions.AlreadyExistsException:
        response = cloudformation_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
        )
        print('Stack update initiated.')
    return response

bucket_name = generate_valid_bucket_name()
region = 'eu-north-1'

# Create S3 bucket
print(f'Creating S3 bucket: {bucket_name} in region: {region}...')
create_bucket(bucket_name, region)
print(f'S3 bucket created: {bucket_name}')

# Zip Lambda function files
print(f'Zipping {ENTRY_FUNCTION_NAME}...')
zip_lambda_function(ENTRY_FUNCTION_NAME, ENTRY_ZIP)
print(f'Zipping {EXIT_FUNCTION_NAME}...')
zip_lambda_function(EXIT_FUNCTION_NAME, EXIT_ZIP)

# Upload ZIP files to S3
print(f'Uploading {ENTRY_ZIP} to S3...')
upload_to_s3(ENTRY_ZIP, bucket_name, ENTRY_ZIP)
print(f'Uploading {EXIT_ZIP} to S3...')
upload_to_s3(EXIT_ZIP, bucket_name, EXIT_ZIP)

# Deploy CloudFormation stack
print(f'Deploying CloudFormation stack: {STACK_NAME}...')
deploy_cloudformation_stack(TEMPLATE_FILE, STACK_NAME)
print('Deployment complete.')
