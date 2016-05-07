LAMBDA_FUNC ?= fb-webhook-handler
BASE_IMAGE = lambda-test-base
TEST_IMAGE = lambda-test
TEST_CONTAINER = lambda-test

.base-image:
	(docker images | grep $(BASE_IMAGE)) || docker build --tag=$(BASE_IMAGE) --rm=true --force-rm=true aws/lambda/tests/base-image | tee aws/lambda/tests/base-image/build.log

.test-image: .base-image
	if [ -e "aws/lambda/tests/test-image/lambda" ]; then rm -rf aws/lambda/tests/test-image/lambda; fi
	mkdir aws/lambda/tests/test-image/lambda
	cp aws/lambda/lambda.zip aws/lambda/tests/test-image/lambda
	cd aws/lambda/tests/test-image/lambda && unzip -q lambda.zip
	rm aws/lambda/tests/test-image/lambda/lambda.zip
	(docker ps -a | awk '$$NF == "$(TEST_CONTAINER)" {exit 1}') || docker rm -f $(TEST_CONTAINER)
	(docker images | awk '$$NF == "$(TEST_IMAGE)" {exit 1}') || docker rmi $(TEST_IMAGE)
	rm -f aws/lambda/tests/test-image/build.log
	rm -f aws/lambda/tests/tests.log
	docker build --tag=$(TEST_IMAGE) --no-cache --rm=true --force-rm=true aws/lambda/tests/test-image | tee aws/lambda/tests/test-image/build.log

.test-package: .test-image
	docker run -it --name=$(TEST_CONTAINER) $(TEST_IMAGE) | tee aws/lambda/tests/tests.log

.package:
	rm -f aws/lambda/lambda.zip
	cd aws/lambda && zip --quiet -r lambda.zip . -x \*.pyc -x \*.example -x tests/test-image/\* -x tests/base-image/\*

.upload:
	aws lambda update-function-code --function-name $(LAMBDA_FUNC) --zip-file fileb://aws/lambda/lambda.zip

.test-gateway:
	cd aws/api-gateway/tests && python test_gateway.py

lambda: .package .test-package .upload .test-gateway

test-lambda: .package .test-package

test-shell: .package .test-image
	docker run -it --name=$(TEST_CONTAINER) --entrypoint=/bin/bash $(TEST_IMAGE)
