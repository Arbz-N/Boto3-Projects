import json


def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))
    # Log the full event for debugging — visible in CloudWatch Logs

    # State Machine uses "Payload.$":"$" which wraps the input
    # Lambda receives: {"Payload": {"orderId":..., "customerId":...}}
    # So we extract from inside Payload
    payload = event.get('Payload', event)
    # Use Payload if present, otherwise fall back to event directly

    order_id    = payload.get('orderId')
    customer_id = payload.get('customerId')
    # .get() is safe — returns None if key is missing, no crash

    print(f"Processing order {order_id} for customer {customer_id}")

    return {
        'statusCode':  200,
        'message':     'Order processed successfully',
        'order_id':    order_id,
        'customer_id': customer_id
    }