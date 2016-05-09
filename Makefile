LAMBDA_FUNC ?= fb-webhook-handler
BASE_IMAGE = webhook-test-base
TEST_IMAGE = webhook-test
TEST_CONTAINER = webhook-test

.base-image:
	(docker images | grep $(BASE_IMAGE)) || docker build --tag=$(BASE_IMAGE) --rm=true --force-rm=true webhook/tests/base-image | tee webhook/tests/base-image/build.log

.test-image: .base-image
	cp -f package/webhook.zip webhook/tests/test-image/
	(docker ps -a | awk '$$NF == "$(TEST_CONTAINER)" {exit 1}') || docker rm -f $(TEST_CONTAINER)
	(docker images | awk '$$NF == "$(TEST_IMAGE)" {exit 1}') || docker rmi $(TEST_IMAGE)
	rm -f webhook/tests/test-image/build.log
	rm -f webhook/tests/tests.log
	docker build --tag=$(TEST_IMAGE) --no-cache --rm=true --force-rm=true webhook/tests/test-image | tee webhook/tests/test-image/build.log
	rm -f webhook/tests/test-image/webhook.zip

.test-package: .test-image
	docker run -it --name=$(TEST_CONTAINER) $(TEST_IMAGE) | tee webhook/tests/tests.log

.package-webhook:
	if [ ! -e package ]; then mkdir package; else rm -rf package/*; fi
	cd webhook && zip --quiet -r ../package/webhook.zip . -x \*.pyc -x \*.example -x tests/test-image/\* -x tests/base-image/\*

# AWS lambda

.test-api-gateway:
	cd aws/api-gateway/tests && python test_gateway.py

.package-lambda:
	zip --quiet -j package/webhook.zip aws/lambda/webhook.py

.upload-lambda:
	aws lambda update-function-code --function-name $(LAMBDA_FUNC) --zip-file fileb://package/webhook.zip

lambda: .package-webhook .package-lambda .test-package .upload-lambda .test-api-gateway

test-lambda: .package-webhook .package-lambda .test-package

test-lambda-shell: .package-webhook .package-lambda .test-image
	docker run -it --name=$(TEST_CONTAINER) --entrypoint=/bin/bash $(TEST_IMAGE)
