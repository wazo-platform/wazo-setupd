# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_setupd.http import AuthResource
from xivo.auth_verifier import required_acl


class ConfigResource(AuthResource):

    def __init__(self, config):
        self._config = config

    @required_acl('setupd.config.read')
    def get(self):
        return dict(self._config), 200
