import json
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

from utils import get_order

# Globals
order_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')


def _default(o):
    if isinstance(o, Decimal):
        return float(o) if o % 1 else int(o)
    raise TypeError(f"Cannot serialize {type(o)}")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {},
        "body": json.dumps(body, default=_default)
    }


def edit_order(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    order_id = event['pathParameters']['orderId']
    new_data = json.loads(event['body'], parse_float=Decimal)
    new_data['userId'] = user_id
    new_data['orderId'] = order_id

    ddb_item = {
        'orderId': order_id,
        'userId': user_id,
        'data': new_data
    }

    table = dynamodb.Table(order_table)
    table.put_item(
        Item=ddb_item,
        ConditionExpression="attribute_exists(orderId) AND attribute_exists(userId) AND #data.#status = :status",
        ExpressionAttributeNames={
            "#data": "data",
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "PLACED"
        }
    )

    return get_order(user_id, order_id)


def lambda_handler(event, context):
    try:
        updated = edit_order(event)
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return _response(400, {
                "message": "Cannot edit this order. Check that the order exists and its status is PLACED."
            })
        raise
    return _response(200, updated)
