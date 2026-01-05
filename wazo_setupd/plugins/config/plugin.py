# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec

from .http import ConfigResource


class Plugin:
    def register_spec(self, spec: APISpec):
        spec.path(resource=ConfigResource, path='/config')

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        spec: APISpec = dependencies['spec']

        api.add_resource(ConfigResource, '/config', resource_class_args=[config])

        self.register_spec(spec)
