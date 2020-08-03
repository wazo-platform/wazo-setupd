FROM python:3.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN python -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY . /usr/src/wazo-setupd
WORKDIR /usr/src/wazo-setupd
RUN pip install -r requirements.txt
RUN python setup.py install

FROM python:3.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-setupd /etc/wazo-setupd
RUN true \
    && adduser --quiet --system --group --home /var/lib/wazo-setupd wazo-setupd \
    && mkdir -p /etc/wazo-auth/conf.d \
    && mkdir -p /etc/wazo-nestbox-plugin/conf.d \
    && mkdir -p /etc/wazo-setupd/conf.d \
    && mkdir -p /etc/wazo-webhookd/conf.d \
    && mkdir -p /usr/share/wazo-setupd \
    && install -m 0640 -o wazo-setupd -g root /dev/null /usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml \
    && ln -s /usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml /etc/wazo-auth/conf.d/50-wazo-plugin-nestbox.yml \
    && ln -s /usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml /etc/wazo-nestbox-plugin/conf.d/50-wazo-plugin-nestbox.yml \
    && ln -s /usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml /etc/wazo-webhookd/conf.d/50-wazo-plugin-nestbox.yml \
    && install -o wazo-setupd -g wazo-setupd /dev/null /var/log/wazo-setupd.log

EXPOSE 9302

ENV PYTHONUNBUFFERED=TRUE

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-setupd"]
