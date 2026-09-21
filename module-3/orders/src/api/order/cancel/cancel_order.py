import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


# Custom exception
class OrderStatusError(Exception):
    status_code = 400


# Globals
orders_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')


def _default(o):
    if isinstance(o, Decimal):
        return float(o) if o % 1 else int(o)
    raise TypeError(f"Cannot serialize {type(o)}")


def cancel_order(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    order_id = event['pathParameters']['orderId']

    # Orders are stored with ISO-8601 UTC timestamps, so an ISO cutoff compares correctly
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()

    table = dynamodb.Table(orders_table)
    try:
        response = table.update_item(
            Key={'userId': user_id, 'orderId': order_id},
            UpdateExpression="set #data.#status = :new_status",
            ConditionExpression="#data.#status = :current_status AND #data.#orderTime > :minOrderTime",
            ExpressionAttributeNames={
                "#data": "data",
                "#status": "status",
                "#orderTime": "orderTime"
            },
            ExpressionAttributeValues={
                ":current_status": "PLACED",
                ":minOrderTime": cutoff,
                ":new_status": "CANCELED"
            },
            ReturnValues="ALL_NEW"
        )
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise OrderStatusError(
                f"Order {order_id} cannot be cancelled. Make sure the status of this order "
                "is PLACED and it was created less than 10 minutes ago."
            )
        raise

    return response['Attributes']['data']


def lambda_handler(event, context):
    try:
        updated = cancel_order(event)
    except OrderStatusError as oe:
        return {
            "statusCode": oe.status_code,
            "headers": {},
            "body": json.dumps({"message": str(oe)})
        }
    return {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(updated, default=_default)
    }
