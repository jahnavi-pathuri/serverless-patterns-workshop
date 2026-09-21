# Module 3 - Synchronous Invocation + Idempotence (Orders Service)

This is my work for Module 3 of the AWS Serverless Patterns workshop (SAM + Python).

In this module I built an Orders API. The API has five small Lambda functions, and each function does only one job. Users log in with Amazon Cognito. Orders are saved in DynamoDB. I also added idempotence, structured logging and custom metrics with Powertools for AWS Lambda.

Region: `us-east-1` (N. Virginia)

---

## What is in this folder

```
module-3/
├── template.yaml          Base stack from the workshop
├── module3_setup.sh       Setup script from the workshop
├── users/                 Users service and Cognito (from the workshop)
└── orders/                My work for this module
    ├── template.yaml
    ├── src/
    │   ├── api/order/
    │   │   ├── create/create_order.py
    │   │   ├── get/get_order.py
    │   │   ├── list/list_orders.py
    │   │   ├── edit/edit_order.py
    │   │   └── cancel/cancel_order.py
    │   └── layers/utils.py
    └── tests/integration/  (conftest.py and test_api.py)
```

The `orders` stack needs the base stack (`ws-serverless-patterns`) to be deployed first. The base stack gives the Cognito User Pool.

---

## The API

|Function|Method and path|What it does|
|---|---|---|
|Add Order|`POST /orders`|Saves a new order|
|List Orders|`GET /orders`|Returns all orders of the user|
|Get Order|`GET /orders/{orderId}`|Returns one order|
|Edit Order|`PUT /orders/{orderId}`|Changes an order (only if status is PLACED)|
|Cancel Order|`DELETE /orders/{orderId}`|Cancels an order (status PLACED, less than 10 minutes old)|

All routes need a Cognito ID token in the `Authorization` header. Without a token, the API gives 401.

---

## What I did in each step

**1. Create the Orders service** I made the Orders table, the API and the Add Order function. Then I added the tests. I wrote the Get, List, Edit and Cancel functions one by one, and I ran the tests after each one.

**1.2 Lambda layer** The shared code is in `src/layers/utils.py` and is deployed as the `pyutils` layer. It has a `get_order()` function. Get, Edit and Cancel use this layer, so I did not repeat the code.

**2. Idempotence** Add Order uses `@idempotent_function` from Powertools. The key is the `orderId` in the request body. The first result is saved in a DynamoDB table (`IdempotencyTable`). If the same request comes again, the saved result is returned and no new order is created. The records expire after one hour (this is the default).

**3. Structured logging** Add Order uses `Logger` from Powertools. The logs are JSON, so they are easy to search in CloudWatch. The function also logs the Lambda context, like the function name and request ID.

**4. Metrics** Add Order sends two custom metrics with `Metrics` from Powertools:

- `SuccessfulOrder` - one for each new order
- `OrderTotal` - the total amount of the order

The namespace is `ServerlessWorkshop`.

---

## Why idempotence is useful here

The idempotency test sends the same order three times. All three answers have the same `orderId`, and the table has only one new order. Without idempotence, a retry (for example after a network problem) can make a duplicate order, or the function can fail with a duplicate key error. Then the customer cannot know if the order was placed.

---

## What I changed from the workshop

The workshop code was made for its own starter files, and I ran it on a Mac. So I changed some things:

- The workshop page "1 - Create Orders service" was not available to me, so I wrote the first `template.yaml` and the Add Order function myself. I made them match what the tests need.
- The workshop code uses `simplejson`, but Lambda does not have it. I used the standard `json` module and a small helper for Decimal numbers.
- I used my own API name (`OrdersApi`) in the template.
- In the Cancel function, I compare the order time as a text timestamp (ISO format), because that is how I save it.
- The Edit and Cancel functions return a clear 400 message when the order cannot be changed.
- I did not push `.venv`, `.aws-sam` or `samconfig.toml`.

---

## How to deploy and test

Run these from the `orders` folder.

```bash
# 1. Deploy the base stack first (from the module-3 folder)
sam build
sam deploy --guided --stack-name ws-serverless-patterns --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

# 2. Deploy the orders stack (use your own User Pool ID)
cd orders
sam build
sam deploy --stack-name ws-serverless-patterns-orders --region us-east-1 \
  --capabilities CAPABILITY_IAM --resolve-s3 \
  --parameter-overrides UserPoolId=<your-user-pool-id>

# 3. Run the tests
export USERS_STACK_NAME=<your users stack name>
export ORDERS_STACK_NAME=ws-serverless-patterns-orders
python -m pytest tests/integration -v
```

Result: **8 passed**.

---

## How to check logs and metrics

**Logs:** Lambda console -> Applications -> `ws-serverless-patterns-orders` -> AddOrderFunction -> Monitor -> Logs. Open the newest log stream. You can see JSON rows like `"message":"Adding a new order"`.

**Metrics:** CloudWatch console (us-east-1) -> Metrics -> All metrics -> Custom namespaces -> `ServerlessWorkshop` -> `service`. Select `SuccessfulOrder` and `OrderTotal`. Use Sum and a 5 minute period. The data can take 5 to 7 minutes to show.

---

## Problems I had and how I fixed them

- **403 or KeyError right after a deploy:** The new API route needs about one minute to be ready. I waited and ran the tests again.
- **pytest crashed with a `langsmith` error:** The Mac had a broken global pytest. I used `python -m pytest` inside the virtual environment.
- **`wget: command not found`:** The workshop script needs `wget`. I installed it with `brew install wget`.
- **Nothing in the console:** The console was in a different region. I changed it to N. Virginia (us-east-1).

---

## Clean up

I delete the stacks in this order, after everyone in the team has the screenshots:

1. `ws-serverless-patterns-orders`
2. `ws-serverless-patterns` (this also deletes the users stack)
