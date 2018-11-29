# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import requests


class DeploydMockClient:

    def __init__(self, host, port):
        self._host = host
        self._port = port

    def url(self, *parts):
        return 'https://{host}:{port}/{path}'.format(host=self._host,
                                                     port=self._port,
                                                     path='/'.join(parts))

    def reset(self):
        requests.post(self.url('_reset'), verify=False)

    def requests(self):
        return requests.get(self.url('_requests'), verify=False)

    def set_post_instance(self, response):
        body = {'response': 'post_instance',
                'content': response}
        requests.post(
            self.url('_set_response'),
            json=body,
            verify=False,
        )
