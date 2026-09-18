# Module 1: Intro to Serverless

This module introduced the basic components of a serverless application using AWS Lambda, Amazon DynamoDB, and Amazon API Gateway.

## Resources created

- DynamoDB table: `serverless_workshop_intro`
- Partition key: `_id`
- Lambda function: `first-function`
- Lambda function: `m1-add-sample-data`
- Lambda function: `get-users`
- API Gateway REST API: `ServerlessREST`
- API resource: `/users`
- API method: `GET`
- API stage: `v1`

## What was completed

1. Created the DynamoDB table.
2. Added an item manually through the DynamoDB console.
3. Created and tested the `first-function` Lambda function.
4. Created the `m1-add-sample-data` Lambda function.
5. Added DynamoDB permissions to the Lambda execution role.
6. Inserted sample user records into DynamoDB.
7. Created the `get-users` Lambda function.
8. Created a REST API with API Gateway.
9. Connected the `GET /users` method to the `get-users` Lambda function.
10. Deployed and tested the API.

## Result

The deployed API successfully returned user records stored in DynamoDB.

## Screenshot

The Module 1 result screenshot is stored in:

`screenshots/module-1-result.png`