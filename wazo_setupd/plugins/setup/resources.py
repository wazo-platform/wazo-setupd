# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from wazo_setupd.rest_api import ErrorCatchingResource
from xivo.auth_verifier import required_acl

from .schema import setup_schema


class SetupResource(ErrorCatchingResource):

    def __init__(self, service):
        self.service = service

    @required_acl('setupd.setup.create')
    def post(self):
        setup_infos = setup_schema.load(request.json).data

        self.service.setup(setup_infos)

        return {}, 201
