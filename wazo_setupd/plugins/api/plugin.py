# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec

from .http import OpenAPIResource


class Plugin:
    def register_spec(self, spec: APISpec):
        spec.path(resource=OpenAPIResource, path='/api/api.yml')

    def load(self, dependencies):
        api = dependencies['api']
        spec = dependencies['spec']

        api.add_resource(OpenAPIResource, '/api/api.yml', resource_class_args=[spec])

        self.register_spec(spec)
