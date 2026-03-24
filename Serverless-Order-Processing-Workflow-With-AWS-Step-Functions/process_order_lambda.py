import json


def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))
    payload = event.get('Payload', event)
    order_id    = payload.get('orderId')
    customer_id = payload.get('customerId')
    print(f"Processing order {order_id} for customer {customer_id}")

    return {
        'statusCode':  200,
        'message':     'Order processed successfully',
        'order_id':    order_id,
        'customer_id': customer_id
    }