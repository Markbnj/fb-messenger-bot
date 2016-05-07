FROM lambda-test-base
MAINTAINER Mark Betz <betz.mark@gmail.com>

ADD lambda /usr/local/bin/lambda

WORKDIR /usr/local/bin/lambda/tests

ENTRYPOINT ["python", "test_lambda.py"]