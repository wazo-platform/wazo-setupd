FROM python:3.5.3

ADD . /usr/src/wazo-setupd
ADD ./contribs/docker/certs /usr/share/xivo-certs

WORKDIR /usr/src/wazo-setupd

RUN true \
    && adduser --quiet --system --group wazo-setupd \
    && mkdir -p /etc/wazo-setupd/conf.d \
    && install -o wazo-setupd -g wazo-setupd -d /var/run/wazo-setupd \
    && touch /var/log/wazo-setupd.log \
    && chown wazo-setupd:wazo-setupd /var/log/wazo-setupd.log \
    && pip install -r requirements.txt \
    && python setup.py install \
    && cp -r etc/* /etc \
    && apt-get -yqq autoremove \
    && openssl req -x509 -newkey rsa:4096 -keyout /usr/share/xivo-certs/server.key -out /usr/share/xivo-certs/server.crt -nodes -config /usr/share/xivo-certs/openssl.cfg -days 3650

EXPOSE 9302

CMD ["wazo-setupd"]
