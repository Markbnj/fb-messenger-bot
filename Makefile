LAMBDA_FUNC ?= fb-webhook-handler

.test-package:
	$(eval TEST_DIR := $(shell mktemp -d))
	cp aws/lambda/lambda.zip $(TEST_DIR)/
	cd $(TEST_DIR) && unzip -q lambda.zip
	cd $(TEST_DIR)/tests && nosetests test_lambda.py
	rm -rf $(TEST_DIR)

.package:
	rm -f aws/lambda/lambda.zip
	cd aws/lambda && zip --quiet -r lambda.zip . -x \*.pyc -x \*.example

.upload:
	aws lambda update-function-code --function-name $(LAMBDA_FUNC) --zip-file fileb://aws/lambda/lambda.zip

.test-gateway:
	cd aws/api-gateway/tests && nosetests test_gateway.py

lambda: .package .test-package .upload .test-gateway
