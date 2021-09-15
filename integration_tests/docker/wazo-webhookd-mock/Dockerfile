FROM p0bailey/docker-flask

MAINTAINER Wazo Maintainers <dev@wazo.community>

COPY requirements.txt /tmp/requirements.txt
RUN true && \
    pip install -r /tmp/requirements.txt && \
    mkdir -p /etc/wazo-webhookd/conf.d && \
    true

EXPOSE 9300
COPY wazo-webhookd-mock.py /usr/local/bin/wazo-webhookd-mock.py
CMD ["/usr/local/bin/wazo-webhookd-mock.py", "9300"]
