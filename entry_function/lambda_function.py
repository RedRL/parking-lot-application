import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('TABLE_NAME', 'ParkingRecords'))


def entry_handler(event, context):
    license_plate = event['queryStringParameters']['plate']
    parking_lot_id = event['queryStringParameters']['parkingLot']

    # Check if the car is already parked in a lot
    existing_entries = table.scan(
        FilterExpression='licensePlate = :plate AND exitTime = :null',
        ExpressionAttributeValues={':plate': license_plate, ':null': None}
    )
    if existing_entries['Items']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Car is already parked in a lot'})
        }

    ticket_id = generate_sequential_ticket_id()
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
    
def generate_sequential_ticket_id():
    # Scan for the highest ticket ID and generate the next one
    response = table.scan(
        ProjectionExpression="ticketId"
    )
    items = response.get('Items', [])
    max_ticket_id = max(int(item['ticketId']) for item in items) if items else 0
    return str(max_ticket_id + 1).zfill(4)
