# Module 5 - Polling (Order Status Service)

This is my work for Module 5 of the AWS Serverless Patterns workshop (SAM + Python).

In this module a restaurant sends an "order updated" event to an Amazon EventBridge event bus. A Lambda function receives the event and changes the order status in DynamoDB. The customer app does not wait for this. It asks the API for the status again and again (polling) until the status changes.

Region: `us-east-1` (N. Virginia)

This module uses the stacks from Module 3. It uses the same Orders table and the same Cognito User Pool. Please deploy Module 3 first.

---

## What is in this folder

```
module-5/
├── template.yaml                     Event bus, Lambda function and rule
├── requirements.txt
├── polling-api.sh                    Script that checks the order status again and again
├── src/api/update_order_status.py    Lambda function
├── events/                           Sample events
└── tests/integration/
    ├── conftest.py                   Test setup (creates a test user)
    ├── test_order.py                 The 2 integration tests
    ├── order.json
    └── updated-order.json
```

---

## How it works

1. The restaurant sends an event to the `Orders-dev` event bus. The event has `source = restaurant` and `detail-type = order.updated`.
2. An EventBridge rule finds this event and starts `UpdateOrderStatusFunction`.
3. The function changes the order `status` in the Orders table (the one from Module 3).
4. The customer app calls `GET /orders/{orderId}` on the Orders API from time to time. When the status is the one it wants, it stops.

The template has these resources:

- `RestaurantBus` - the event bus (`Orders-dev`)
- `UpdateOrderStatusFunction` - the Lambda function, with a rule for the events above

The function needs two inputs: the Orders table name and the User Pool ID. They are template parameters.

---

## Why polling and not waiting

The order update does not happen at the same time as the customer request. The restaurant can update the order after a few seconds or after many minutes. If the caller waits with one open connection, the connection can time out, and it uses resources the whole time. With polling, each request is short and gets an answer right away. The caller can also stop and start again without losing anything, because the status is saved in DynamoDB.

---

## What I changed from the workshop

- I added `CodeUri: src/api/` to the function, and I changed the handler to `update_order_status.lambda_handler`. This way only the function folder is packaged.
- I used the Powertools layer version that already worked in Module 3 (`AWSLambdaPowertoolsPythonV2:68`).
- I made the policy a list, like in my other templates.
- The workshop page sends you to Module 2 for the login token. I made a test user with the AWS CLI and got the ID token from Cognito.
- The API URL has no slash at the end, so I used `${URL}/orders/O2` for polling.
- I made `events/event-new-order.json` myself, with the fields that my Add Order function needs.
- In the update event, I used the Cognito user `sub` as `userId`, because the Orders table uses it as the key.
- I did not push `.venv`, `.aws-sam` or `samconfig.toml`.

---

## How to deploy

Run these from this folder. Use your own values.

```bash
# Find the two values from the Module 3 stacks
ORDERS_TABLE=$(aws cloudformation describe-stacks --stack-name ws-serverless-patterns-orders \
  --query "Stacks[0].Outputs[?OutputKey=='OrdersTable'].OutputValue" --output text)
USER_POOL=$(aws cloudformation describe-stacks --stack-name <your users stack name> \
  --query "Stacks[0].Outputs[?OutputKey=='UserPool'].OutputValue" --output text)

# Build and deploy
sam build
sam deploy --stack-name ws-serverless-patterns-polling --region us-east-1 \
  --capabilities CAPABILITY_IAM --resolve-s3 \
  --parameter-overrides OrdersTablename=$ORDERS_TABLE UserPool=$USER_POOL
```

To check that it worked:

```bash
aws events list-event-buses --query "EventBuses[].Name"     # should show Orders-dev
aws events list-rules --event-bus-name Orders-dev            # should show the rule as ENABLED
```

---

## How to run the tests

```bash
export ORDER_STATUS_STACK_NAME=ws-serverless-patterns-polling
export ORDERS_STACK_NAME=ws-serverless-patterns-orders
export CLIENT_ID=<your Cognito app client ID>
python -m pytest tests/integration -v
```

Result: **2 passed**.

- `test_order_status` - the customer can read the order status.
- `test_order_update_process` - the restaurant sends an event, and then the API shows the new status.

---

## How to run the polling demo

1. Make a test user in Cognito and get an ID token. Save it in `ID_TOKEN`. Save the API URL in `URL`.
2. Create a test order:
    
    ```bash
    curl -X POST -H "Authorization:$ID_TOKEN" -H "Content-Type: application/json" \  -d @events/event-new-order.json $URL/orders
    ```
    
3. Start polling in one terminal:
    
    ```bash
    sh ./polling-api.sh ${URL}/orders/O2 $ID_TOKEN
    ```
    
    It prints `Still waiting for IN-PROCESS status` again and again.
4. In a second terminal, send the restaurant update:
    
    ```bash
    aws events put-events --entries file://events/test-order-update.json
    ```
    
    The answer should have `FailedEntryCount: 0`.
5. Go back to the first terminal. After a few seconds it prints `Order status matches desired result of IN-PROCESS. Polling is complete!`

---

## Problems I had and how I fixed them

- **Empty `module5_setup.sh` file:** The download link was cut off, so `wget` made an empty file. I downloaded it again with `curl -fL`, and then I checked the file size.
- **`tests/requirements.txt` was empty:** The workshop gives the content on the "Set up tests" page. I added it there.
- **The polling script runs a long time:** This is normal. It stops only after the event is sent.

---

## Clean up

I delete the stacks in this order, after everyone in the team has the screenshots:

1. `ws-serverless-patterns-polling`
2. `ws-serverless-patterns-orders`
3. `ws-serverless-patterns` (this also deletes the users stack and the test users)
