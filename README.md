# Parking Lot Application

This repository contains the code and deployment script for a Parking Lot application using AWS Lambda, DynamoDB, and API Gateway. The application allows users to manage parking lot entries and exits, and calculate the parking charges.

## Prerequisites

Before you begin, ensure you have the following:

1. **AWS Account**: Ensure you have an AWS account with an IAM user that has the necessary permissions.
2. **AWS CLI**: Installed and configured with the necessary permissions.
3. **Python**: Installed on your machine.
4. **Boto3**: AWS SDK for Python (can be installed via `pip install boto3`).
5. **Git**: Installed on your machine.

## Repository Contents

- `entry/`: Contains the Lambda function code for the entry handler.
  - `lambda_function.py`: Entry function code.
- `exit/`: Contains the Lambda function code for the exit handler.
  - `lambda_function.py`: Exit function code.
- `template.yaml`: CloudFormation template to define the infrastructure.
- `deploy.py`: Python script to deploy the CloudFormation stack and Lambda functions.

## Cloning the Repository

Clone the repository to your local machine using the following command:

```sh
git clone https://github.com/YourUsername/parking-lot-application.git
cd parking-lot-application
```

## Deployment Instructions

To deploy the application, follow these steps:

1. **Ensure AWS CLI is configured** with the necessary permissions.

2. **Run the Deployment Script**:
   ```sh
   python deploy.py
   ```

   The deployment script will perform the following actions:
   - Create a unique S3 bucket to store Lambda function code.
   - Zip the Lambda function files.
   - Upload the ZIP files to the S3 bucket.
   - Deploy a CloudFormation stack to create the necessary AWS resources, including a DynamoDB table for storing data.

## Accessing the API

After deployment, the API Gateway endpoints will be created for the entry and exit methods. Follow these steps to find the URLs:

1. **Log into the AWS Management Console**:
   Go to the AWS Management Console and navigate to the API Gateway service.

2. **Select the Deployed API**:
   Find the API named `ParkingLotAPI` or similar.

3. **Find the Stage URL**:
   In the API Gateway console, select the API and then select the "Stages" section. Here, you will find the deployed stages (e.g., `prod`).

4. **Get the Base URL**:
   The base URL will look something like this:
   ```
   https://<api-id>.execute-api.<region>.amazonaws.com/prod/
   ```

### Example Usage

#### Entry Method

To create an entry record, use the following URL format:

```sh
curl -X POST "https://<api-id>.execute-api.<region>.amazonaws.com/prod/entry?plate=XYZ123&parkingLot=LotA"
```

This will return a JSON response with the ticket ID.

#### Exit Method

To record an exit and calculate the charge, use the following URL format:

```sh
curl -X POST "https://<api-id>.execute-api.<region>.amazonaws.com/prod/exit?ticketId=<ticket-id>"
```

This will return a JSON response with the total parked time and the charge.

## Data Storage

All parking lot data is stored in a DynamoDB table. This includes information about entry and exit times, license plates, and charges.

## Cleaning Up

To delete the stack and clean up the resources created, follow these instructions in the AWS Management Console:

1. **Log into the AWS Management Console**:
   Go to the AWS Management Console and navigate to the CloudFormation service.

2. **Select the Stack**:
   Find the stack named `ParkingLotStack` or similar.

3. **Delete the Stack**:
   Select the stack and choose "Delete".