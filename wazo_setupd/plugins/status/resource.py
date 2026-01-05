# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.auth_verifier import required_acl

from wazo_setupd.http import AuthResource


class StatusResource(AuthResource):
    def __init__(self, status_aggregator):
        self.status_aggregator = status_aggregator

    @required_acl('setupd.status.read')
    def get(self):
        """
        ---
        tags:
          - status
        operationId: getStatus
        summary: Print infos about internal status of wazo-setupd
        description: |
          Returns the internal health status of wazo-setupd and its components.

          **Required ACL:** `setupd.status.read`
        security:
          - wazo_auth_token:
            - setupd.status.read
        responses:
          200:
            description: The internal infos of wazo-setupd
            content:
              application/json:
                schema: StatusSummarySchema
          401:
            $ref: '#/components/responses/InvalidRequest'
        """
        return self.status_aggregator.status(), 200
