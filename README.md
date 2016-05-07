# lambda-messenger-bot

### A project for easy dev/deployment of an FB messenger bot running on AWS lambda and using API Gateway as an entrypoint.

#### Roadmap

  - Create interface to get user profile
  - Create interfaces to send simple and structured messages
  - Implement interface to DynamoDB or another store for sessions
  - Implement interface to wit.ai at pluggable abstraction level
  - Create swagger definition of API gateway setup
  - Create make targets to build/configurfe the gateway
  - Create make targets to create the lambda function
  - Support persistent user prefs keyed on page-scoped user id (dynamodb? elasticache?)
