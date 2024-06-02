import json
from decimal import Decimal
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ParkingRecords')


def lambda_handler(event, context):
    ticket_id = event['queryStringParameters']['ticketId']

    response = table.get_item(Key={'ticketId': ticket_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Ticket not found'})
        }

    item = response['Item']
    entry_time = item['entryTime']
    exit_time = int(datetime.now().timestamp())

    table.update_item(
        Key={'ticketId': ticket_id},
        UpdateExpression="set exitTime=:e",
        ExpressionAttributeValues={':e': exit_time}
    )

    total_time_seconds = exit_time - entry_time

    # Convert total time to hours, minutes, and seconds
    total_hours = total_time_seconds // 3600
    total_minutes = (total_time_seconds // 60) % 60
    total_seconds = total_time_seconds % 60

    total_time_string = '{:02}:{:02}:{:02}'.format(total_hours, total_minutes, total_seconds)

    charge = float(total_time_seconds // 900 + 1) * 2.5  # $10 per hour, $2.5 per 15 minutes

    return {
        'statusCode': 200,
        'body': json.dumps({
            'licensePlate': item['licensePlate'],
            'totalParkedTime': total_time_string,
            'parkingLotId': item['parkingLotId'],
            'charge': charge
        })
    }
