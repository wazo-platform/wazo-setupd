# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import OpenAPIResource


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        spec = dependencies['spec']

        api.add_resource(OpenAPIResource, '/api/api.yml', resource_class_args=[spec])
