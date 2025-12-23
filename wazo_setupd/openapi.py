# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_flask_restful import RestfulPlugin

API_VERSION = '1.0'


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
    plugins=[RestfulPlugin(), MarshmallowPlugin()],
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

# Add common response components
SPEC.components.response(
    'InvalidRequest',
    {'description': 'Invalid request body or parameters'},
)

SPEC.components.response(
    'InternalServerError',
    {'description': 'An internal server error occurred'},
)

SPEC.components.response(
    'ServiceUnavailable',
    {'description': 'A required service is unavailable'},
)
