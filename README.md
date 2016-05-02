# lambda-messenger-bot

### A framework/project easy dev/deployment of an FB messenger bot running on AWS lambda and using API Gateway as an entrypoint.

#### Roadmap

  - Complete test cases for message receipt and auth postbacks
  - Implement message receiver and sender classes in handlers
  - Implement interface to DynamoDB or another store for sessions
  - Implement interface to wit.ai at pluggable abstraction level
  - Create swagger definition of API gateway setup
  - Create make targets to build/configurfe the gateway
  - Create make targets to create the lambda function