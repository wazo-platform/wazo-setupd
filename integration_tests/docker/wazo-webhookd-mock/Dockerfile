FROM p0bailey/docker-flask

MAINTAINER Wazo Maintainers <dev@wazo.community>

COPY server.crt /usr/local/share/ssl/webhookd/server.crt
COPY server.key /usr/local/share/ssl/webhookd/server.key

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

EXPOSE 9300
COPY wazo-webhookd-mock.py /usr/local/bin/wazo-webhookd-mock.py
CMD ["/usr/local/bin/wazo-webhookd-mock.py", "9300"]
