# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec
from xivo.status import Status

from .resource import StatusResource
from .schemas import StatusSummarySchema


class Plugin:
    def register_spec(self, spec: APISpec):
        spec.components.schema('StatusSummary', schema=StatusSummarySchema)
        spec.path(resource=StatusResource, path='/status')

    def load(self, dependencies):
        api = dependencies['api']
        status_aggregator = dependencies['status_aggregator']
        spec: APISpec = dependencies['spec']

        status_aggregator.add_provider(provide_status)

        api.add_resource(
            StatusResource, '/status', resource_class_args=[status_aggregator]
        )

        self.register_spec(spec)


def provide_status(status):
    status['rest_api']['status'] = Status.ok
