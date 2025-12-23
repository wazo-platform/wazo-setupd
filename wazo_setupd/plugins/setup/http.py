# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_setupd.http import ErrorCatchingResource

from .schemas import setup_schema


class SetupResource(ErrorCatchingResource):
    def __init__(self, service):
        self.service = service

    def post(self):
        """Setup the Wazo Engine.
        ---
        tags:
          - setup
        operationId: setupWazoEngine
        summary: Setup the Wazo Engine
        description: |
          Initialize the Wazo Engine with provided configuration.
          This endpoint configures the engine language, admin password, and optionally
          registers with a Nestbox instance for enterprise management.
        requestBody:
          required: true
          content:
            application/json:
              schema: SetupSchema
        responses:
          201:
            description: The setup has been completed
          400:
            $ref: '#/components/responses/InvalidRequest'
          500:
            $ref: '#/components/responses/InternalServerError'
          503:
            $ref: '#/components/responses/ServiceUnavailable'
        """
        setup_infos = setup_schema.load(request.json)

        self.service.setup(setup_infos)

        return {}, 201
