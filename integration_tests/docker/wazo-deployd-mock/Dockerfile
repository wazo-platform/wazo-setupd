FROM python:3.7-slim-bullseye

MAINTAINER Wazo Maintainers <dev@wazo.community>

RUN pip3 install --no-cache-dir flask

COPY wazo-deployd-mock.py /usr/local/bin/wazo-deployd-mock.py
COPY server.crt /usr/local/share/ssl/deployd/server.crt
COPY server.key /usr/local/share/ssl/deployd/server.key

EXPOSE 9800

CMD ["/usr/local/bin/wazo-deployd-mock.py", "9800"]
