.test:
	$(eval TEST_DIR := $(shell mktemp -d))
	cp aws/lambda/lambda.zip $(TEST_DIR)/
	cd $(TEST_DIR) && unzip -q lambda.zip
	cd $(TEST_DIR)/tests && nosetests
	rm -rf $(TEST_DIR)

.package:
	rm -f aws/lambda/lambda.zip
	cd aws/lambda && zip --quiet -r lambda.zip .

lambda: .package .test
