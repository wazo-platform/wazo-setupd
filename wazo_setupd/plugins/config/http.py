# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.auth_verifier import required_acl

from wazo_setupd.auth import required_master_tenant
from wazo_setupd.http import AuthResource


class ConfigResource(AuthResource):
    def __init__(self, config):
        self._config = config

    @required_master_tenant()
    @required_acl('setupd.config.read')
    def get(self):
        """
        ---
        tags:
          - config
        operationId: getConfig
        summary: Show the current configuration
        description: |
          Returns the current configuration of the wazo-setupd service.

          **Required ACL:** `setupd.config.read`

          **Note:** This endpoint is restricted to the master tenant.
        security:
          - wazo_auth_token:
            - setupd.config.read
        responses:
          200:
            description: The configuration of the service
            content:
              application/json:
                schema:
                  type: object
                  additionalProperties: true
          401:
            $ref: '#/components/responses/InvalidRequest'
        """
        return dict(self._config), 200
