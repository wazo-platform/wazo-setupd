# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_setupd.rest_api import AuthResource
from xivo.auth_verifier import required_acl


class StatusResource(AuthResource):

    @required_acl('setupd.status.read')
    def get(self):
        result = {
            'rest-api': {
                'status': 'ok',
            }
        }
        return result, 200
