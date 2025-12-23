# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
from flask import make_response, request
from flask_restful import Resource

from wazo_setupd.openapi import create_spec


class OpenAPIResource(Resource):
    def get(self):
        prefix = request.headers.get('X-Script-Name')
        params = {}
        if prefix:
            # apply reverse proxy config
            params.update(base_path_prefix=prefix, scheme="https")
        spec = create_spec(**params)

        return make_response(
            yaml.dump(spec.to_dict(), default_flow_style=False),
            200,
            {'Content-Type': 'application/x-yaml'},
        )
