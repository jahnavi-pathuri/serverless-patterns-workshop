import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

# Globals
orders_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')


def _default(o):
    if isinstance(o, Decimal):
        return float(o) if o % 1 else int(o)
    raise TypeError(f"Cannot serialize {type(o)}")


def list_orders(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']

    table = dynamodb.Table(orders_table)
    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )

    return [item['data'] for item in response['Items']]


def lambda_handler(event, context):
    orders = list_orders(event)
    return {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps({"orders": orders}, default=_default)
    }
