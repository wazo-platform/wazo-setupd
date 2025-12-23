# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
from apispec import APISpec
from flask import make_response, request
from flask_restful import Resource

from wazo_setupd.openapi import make_server_url


class OpenAPIResource(Resource):
    def __init__(self, spec):
        self.spec: APISpec = spec

    def get(self):
        prefix = request.headers.get('X-Script-Name')
        if prefix:
            server = make_server_url(base_path_prefix=prefix, scheme='https')
        else:
            server = make_server_url()

        self.spec.options['servers'] = [server]

        return make_response(
            yaml.dump(self.spec.to_dict(), default_flow_style=False),
            200,
            {'Content-Type': 'application/x-yaml'},
        )
