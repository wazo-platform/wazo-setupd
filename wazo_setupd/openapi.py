# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from typing import Any

from apispec import APISpec, BasePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_flask_restful import RestfulPlugin

from wazo_setupd.schemas import ErrorSchema

API_VERSION = '1.0'

logger = logging.getLogger(__name__)


def make_server_url(base_path_prefix: str | None = None, scheme: str = 'http') -> dict:
    """Create server URL configuration for OpenAPI spec."""
    path_prefix = (base_path_prefix or '') + f'/{API_VERSION}'
    return {
        'url': f'{scheme}://{{domain}}:{{port}}{path_prefix}',
        'variables': {
            'domain': {
                'default': 'wazo.example.com',
                'description': 'Domain name where the wazo-setupd service is hosted',
            },
            'port': {
                'default': '9302',
                'description': 'Port number where wazo-setupd service is available',
            },
        },
    }


COMMON_RESPONSES = {
    400: {'$ref': '#/components/responses/InvalidRequest'},
    404: {'$ref': '#/components/responses/NotFound'},
    500: {'$ref': '#/components/responses/InternalServerError'},
    503: {'$ref': '#/components/responses/AnotherServiceUnavailable'},
}


class BoilerplatePlugin(BasePlugin):
    def __init__(self, common_responses):
        self.common_responses = dict(common_responses)

    def init_spec(self, spec):
        logger.debug("initing boilerplate plugin")

    def operation_helper(
        self, path: str | None = None, operations: dict | None = None, **kwargs: Any
    ) -> None:
        assert operations
        logger.debug("updating operations with common responses")
        for op, opspec in operations.items():
            for res, respec in self.common_responses.items():
                if res not in opspec['responses']:
                    logger.debug(
                        "adding common response %s to operation %s on path %s",
                        res,
                        op,
                        path,
                    )
                    opspec['responses'][res] = respec


# Shared spec instance - plugins register paths/schemas at load time
SPEC = APISpec(
    title="wazo-setupd",
    version=API_VERSION,
    openapi_version="3.0.2",
    info={
        "description": "Wazo Engine initialization service",
        "contact": {
            "name": "Wazo Dev Team",
            "url": "https://wazo-platform.org/",
            "email": "dev@wazo.community",
        },
        "x-logo": {
            "url": "https://wazo-platform.org/images/logo-black.svg",
            "backgroundColor": "#FAFAFA",
            "altText": "Wazo Logo",
        },
    },
    plugins=[RestfulPlugin(), BoilerplatePlugin(COMMON_RESPONSES), MarshmallowPlugin()],
    servers=[make_server_url()],
)


# Add security scheme for X-Auth-Token header
SPEC.components.security_scheme(
    'wazo_auth_token',
    {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Auth-Token',
    },
)


# Register response schemas
SPEC.components.schema('Error', schema=ErrorSchema)

# Add common response components
SPEC.components.response(
    'InvalidRequest',
    {
        'description': 'Invalid request',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'},
            },
        },
    },
)

SPEC.components.response(
    'NotFound',
    {
        'description': 'The resource requested was not found on the server',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'},
            },
        },
    },
)

SPEC.components.response(
    'AnotherServiceUnavailable',
    {
        'description': (
            'Another service is unavailable (e.g. wazo-auth, wazo-confd, Asterisk, ...)'
        ),
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'},
            },
        },
    },
)

SPEC.components.response(
    'InternalServerError',
    {
        'description': 'An internal server error occurred',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/Error'},
            },
        },
    },
)
