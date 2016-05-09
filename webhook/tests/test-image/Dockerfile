FROM webhook-test-base
MAINTAINER Mark Betz <betz.mark@gmail.com>

ADD webhook.zip /usr/local/bin/webhook/

RUN cd /usr/local/bin/webhook &&\
 unzip -q webhook.zip &&\
 rm webhook.zip

WORKDIR /usr/local/bin/webhook/tests

ENTRYPOINT ["python", "test_webhook.py"]