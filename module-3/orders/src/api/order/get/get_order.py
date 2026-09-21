import json
from decimal import Decimal

from utils import get_order


def _default(o):
    if isinstance(o, Decimal):
        return float(o) if o % 1 else int(o)
    raise TypeError(f"Cannot serialize {type(o)}")


def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    order_id = event['pathParameters']['orderId']

    try:
        order = get_order(user_id, order_id)
    except IndexError:
        return {
            "statusCode": 404,
            "headers": {},
            "body": json.dumps({"message": "Order not found"})
        }

    return {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(order, default=_default)
    }
