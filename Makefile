ACCESS_TOKEN ?= DAgBCwEODQcGCAEHBA8LDk
FB_VERIFY_TOKEN ?= CAEDCgAEAAMJBwsNBAkOBg
FB_PAGE_TOKEN ?= EAAWPRQ5jkk8BAAb6HzcUVGnWjbK0wXUhoumtZAVOoHeQLtZCodmrkwkT8ZB8Y8TLsfPZBJ1KTxHbxjUHalsgzXZBWzce8wKNo5Rk0fjwS740g8UKM0iI8Kh0FBQGr4BZAjTugQoJExFV8WHdxQqs5qGWeYVH5lScEKvOhmJFoBfQZDZD

.test:
	$(eval TEST_DIR := $(shell mktemp -d))
	cp aws/lambda/lambda.zip $(TEST_DIR)/
	cd $(TEST_DIR) && unzip -q lambda.zip
	cd $(TEST_DIR)/tests && nosetests
	rm -rf $(TEST_DIR)

.package:
	echo "{\"accessToken\": \"${ACCESS_TOKEN}\", \"verifyToken\": \"${FB_VERIFY_TOKEN}\", \"pageToken\": \"${FB_PAGE_TOKEN}\"}" > aws/lambda/config/tokens.json
	rm -f aws/lambda/lambda.zip
	cd aws/lambda && zip --quiet -r lambda.zip .

lambda: .package .test
