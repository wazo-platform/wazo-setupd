# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import requests


class SysconfdMockClient(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port

    def url(self, *parts):
        return 'http://{host}:{port}/{path}'.format(host=self._host,
                                                    port=self._port,
                                                    path='/'.join(parts))

    def requests(self):
        return requests.get(self.url('_requests'), verify=False)
