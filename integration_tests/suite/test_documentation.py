# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import requests
import yaml
from openapi_spec_validator import openapi_v30_spec_validator, validate_spec

from .helpers.base import BaseIntegrationTest
from .helpers.wait_strategy import NoWaitStrategy

logger = logging.getLogger('openapi_spec_validator')
logger.setLevel(logging.INFO)


class TestDocumentation(BaseIntegrationTest):
    asset = 'documentation'
    wait_strategy = NoWaitStrategy()

    def _get_api_spec(self):
        port = self.service_port(9302, 'setupd')
        api_url = f'http://127.0.0.1:{port}/1.0/api/api.yml'
        response = requests.get(api_url)
        return yaml.safe_load(response.text)

    def test_documentation_errors(self):
        spec = self._get_api_spec()
        validate_spec(spec, validator=openapi_v30_spec_validator)

    def test_spec_has_required_metadata(self):
        spec = self._get_api_spec()

        # Verify OpenAPI version
        assert spec['openapi'] == '3.0.2'

        # Verify API info
        assert spec['info']['title'] == 'wazo-setupd'
        assert 'version' in spec['info']
        assert 'contact' in spec['info']

        # Verify security scheme exists
        assert 'securitySchemes' in spec.get('components', {})
        assert 'wazo_auth_token' in spec['components']['securitySchemes']

    def test_spec_with_reverse_proxy_headers(self):
        port = self.service_port(9302, 'setupd')
        api_url = f'http://127.0.0.1:{port}/1.0/api/api.yml'

        # Simulate reverse proxy with X-Script-Name header
        response = requests.get(api_url, headers={'X-Script-Name': '/api/setupd'})
        spec = yaml.safe_load(response.text)

        validate_spec(spec, validator=openapi_v30_spec_validator)

        servers = spec.get('servers', [])
        assert len(servers) > 0
        server_url = servers[0].get('url', '')
        assert '/api/setupd' in server_url
        assert server_url.startswith('https://')

    def test_common_response_components_registered(self):
        spec = self._get_api_spec()

        responses = spec.get('components', {}).get('responses', {})

        assert 'InvalidRequest' in responses
        assert 'InternalServerError' in responses
        assert 'ServiceUnavailable' in responses
