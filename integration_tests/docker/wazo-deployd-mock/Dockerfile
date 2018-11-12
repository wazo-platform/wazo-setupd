FROM p0bailey/docker-flask

MAINTAINER Wazo Maintainers <dev@wazo.community>

COPY wazo-deployd-mock.py /usr/local/bin/wazo-deployd-mock.py
COPY server.crt /usr/local/share/ssl/deployd/server.crt
COPY server.key /usr/local/share/ssl/deployd/server.key

VOLUME ["/usr/local/share/ssl"]
EXPOSE 9800

CMD ["/usr/local/bin/wazo-deployd-mock.py", "9800"]
