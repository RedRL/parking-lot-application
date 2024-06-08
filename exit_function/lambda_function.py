import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('TABLE_NAME', 'ParkingRecords'))


def exit_handler(event, context):
    ticket_id = event['queryStringParameters']['ticketId']

    # Fetch the item from the table
    response = table.get_item(Key={'ticketId': ticket_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Ticket not found'})
        }

    item = response['Item']

    # Check if the car has already exited
    if item['exitTime'] is not None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Car has already exited'})
        }

    entry_time = item['entryTime']
    exit_time = int(datetime.now().timestamp())

    # Update the item with the exit time
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

    charge = float(total_time_seconds // 900 + 1) * 2.5  # $2.5 per 15 minutes

    return {
        'statusCode': 200,
        'body': json.dumps({
            'licensePlate': item['licensePlate'],
            'totalParkedTime': total_time_string,
            'parkingLotId': item['parkingLotId'],
            'charge': charge
        })
    }
