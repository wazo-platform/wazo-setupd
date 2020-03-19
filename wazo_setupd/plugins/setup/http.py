# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_setupd.http import ErrorCatchingResource

from .schemas import setup_schema


class SetupResource(ErrorCatchingResource):
    def __init__(self, service):
        self.service = service

    def post(self):
        setup_infos = setup_schema.load(request.json)

        self.service.setup(setup_infos)

        return {}, 201
