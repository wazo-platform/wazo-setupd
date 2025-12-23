# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from dataclasses_jsonschema import JsonSchemaMixin, SchemaType
from dataclasses_jsonschema.type_defs import JsonDict

API_VERSION = '1.0'


def create_spec(
    base_path_prefix: str | None = None, scheme: str | None = 'http', **kwargs
) -> APISpec:
    """Create and configure the OpenAPI specification."""
    base_path_prefix = (base_path_prefix or '') + f'/{API_VERSION}'
    base_path = {
        'url': f'{scheme}://{{domain}}:{{port}}/{base_path_prefix}',
        'variables': {
            'domain': {
                'default': 'wazo.example.com',
                'description': 'domain name where the wazo-setupd service is hosted',
            },
            'port': {
                'default': '9302',
                'description': 'port number where wazo-setupd service is available',
            },
        },
    }

    return APISpec(
        title="wazo-setupd",
        version="1.0.0",
        openapi_version="3.0.3",
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
        servers=[base_path],
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        **kwargs,
    )


def register_dataclass_schema(
    spec: APISpec, name: str | None, dataclass_type: type[JsonSchemaMixin]
) -> JsonDict:
    """Register a dataclass as an OpenAPI schema using dataclasses-jsonschema."""
    name = name or dataclass_type.__name__

    schema = dataclass_type.json_schema(schema_type=SchemaType.OPENAPI_3)
    spec.components.schema(component_id=name, component=schema)
    return schema
