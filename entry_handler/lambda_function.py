import json
import boto3
from datetime import datetime
import random

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ParkingRecords')


def lambda_handler(event, context):
    license_plate = event['queryStringParameters']['plate']
    parking_lot_id = event['queryStringParameters']['parkingLot']
    ticket_id = str(random.randint(1000, 9999))  # Generate random 4-digit number
    entry_time = int(datetime.now().timestamp())

    table.put_item(
        Item={
            'ticketId': ticket_id,
            'licensePlate': license_plate,
            'parkingLotId': parking_lot_id,
            'entryTime': entry_time,
            'exitTime': None
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'ticketId': ticket_id})
    }
