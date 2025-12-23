# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec

from .http import SetupResource
from .schemas import SetupSchema
from .services import SetupService


class Plugin:
    def register_spec(self, spec: APISpec):
        spec.components.schema('SetupSchema', schema=SetupSchema)
        spec.path(resource=SetupResource, path='/setup')

    def load(self, dependencies):
        api = dependencies['api']
        spec: APISpec = dependencies['spec']

        service = SetupService(dependencies['config'], dependencies['stopper'])
        api.add_resource(SetupResource, '/setup', resource_class_args=[service])

        # Register OpenAPI spec
        self.register_spec(spec)
