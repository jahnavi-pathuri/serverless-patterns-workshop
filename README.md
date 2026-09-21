Serverless Patterns Workshop

This repository contains our team’s implementation of Modules 1 through 5 from the AWS Serverless Patterns Workshop.

Team: Code Red

Members:

Usha Sri Dasari

Jahnavi Pathuri

Sainath Reddy Padira

Venkat Golla Chittibabunaidu

Repository: https://github.com/jahnavi-pathuri/serverless-patterns-workshop

Workshop modules

Module 1: Introduction to Serverless

Module 1 introduces the basic AWS serverless services used throughout the workshop. We created a DynamoDB table, added items, created Lambda functions, and connected a Lambda function to an API Gateway REST API.

Main services:

AWS Lambda

Amazon DynamoDB

Amazon API Gateway

AWS IAM

The Module 1 code is in module-1.

Module 2: Synchronous Invocation

Module 2 builds a users service with AWS SAM and Python. API Gateway invokes the Lambda function synchronously, so the caller waits for the function to return a response. The module also adds Amazon Cognito authentication and authorization, unit tests, integration tests, logging, tracing, alarms, and a dashboard.

The Module 2 project is in module-2/ws-serverless-patterns/users.

Module 3: Synchronous Invocation with Idempotence

Module 3 applies the synchronous pattern to an orders service and adds idempotence. The service supports order operations while using an idempotency key to make retries safe. If the same request is received more than once, the service can return the original result instead of creating duplicate data or repeating the operation.

The Module 3 project is in module-3.

Module 4: Asynchronous Invocation

Module 4 demonstrates asynchronous processing. The caller submits work and receives an acknowledgement while the backend continues processing the request. This pattern is useful for tasks that may take longer or do not need to keep the caller waiting for the final result.

The Module 4 project is in module-4.

Module 5: Long Polling for Task Status

Module 5 demonstrates how a client can monitor a long-running task. Instead of keeping the original request open until the task finishes, the client checks a status endpoint using long polling. This keeps the API responsive while still allowing the client to receive the final result.

The Module 5 project is in module-5.

Invocation patterns

Synchronous invocation is useful when the caller needs a result immediately. The caller waits for the service to finish and return a response.

Asynchronous invocation is useful when the work can continue in the background. The caller receives an acknowledgement, and the service completes the work separately.

Idempotence is important when a request might be retried. It prevents a retry from creating duplicate records or applying the same operation more than once.

Long polling is useful when work takes longer than a normal request. The client can ask for status without holding the original request open for the entire duration of the task.

Repository structure

.
├── module-1/
├── module-2/
├── module-3/
├── module-4/
├── module-5/
├── notes/
└── screenshots/

Testing and verification

Each module was tested using the instructions provided in the workshop. The screenshots submitted with the assignment show the successful result for each module.

Before running commands, confirm that the AWS CLI credentials and the intended AWS Region are configured. Review each module’s files for its exact stack name, endpoint, test command, and output values.

Cleanup

After testing, the team deleted the workshop stacks and related AWS resources to prevent unnecessary charges.

AI-tool disclosure

ChatGPT was used for limited assistance with organizing the Git repository, clarifying workshop instructions, and reviewing the wording of the documentation. The team completed and reviewed the AWS implementation, tests, screenshots, and repository contents.
