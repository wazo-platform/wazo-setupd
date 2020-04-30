# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests


class ConfdMockClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def url(self, *parts):
        return 'http://{host}:{port}/{path}'.format(
            host=self._host, port=self._port, path='/'.join(parts)
        )

    def set_wizard_discover(self, response):
        body = {'response': 'wizard_discover', 'content': response}
        requests.post(self.url('_set_response'), json=body)

    def set_wizard(self, response):
        body = {'response': 'wizard', 'content': response}
        requests.post(self.url('_set_response'), json=body)

    def set_rtp(self, response):
        body = {'response': 'asterisk/rtp/general', 'content': response}
        requests.post(self.url('_set_response'), json=body)

    def reset(self):
        requests.post(self.url('_reset'))

    def requests(self):
        return requests.get(self.url('_requests'))
