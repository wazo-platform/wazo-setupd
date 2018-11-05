FROM wazopbx/wazo-setupd

ENV PYTHONDONTWRITEBYTECODE='true'

COPY . /usr/src/wazo-setupd

WORKDIR /usr/src/wazo-setupd
RUN python setup.py develop

CMD ["wazo-setupd", "-d"]
