# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import Mock

from xivo import plugin_helpers
from xivo.status import StatusAggregator

from wazo_setupd.config import _DEFAULT_CONFIG
from wazo_setupd.http_server import api, app
from wazo_setupd.openapi import SPEC
from wazo_setupd.stopper import Stopper

# Paths that should be excluded from OpenAPI spec coverage check
# (e.g., internal endpoints not meant for public API documentation)
EXCLUDED_PATHS = {
    '/static/<path:filename>',  # Flask static files
}


class TestOpenAPISpecCoverage(TestCase):
    """Test that all Flask endpoints are documented in the OpenAPI spec."""

    @classmethod
    def setUpClass(cls):
        """Load all plugins to register Flask routes and spec paths."""
        # Create minimal config for plugins
        config = _DEFAULT_CONFIG

        # Create mock dependencies
        stopper = Mock(spec=Stopper)
        status_aggregator = StatusAggregator()

        # Load all plugins like controller.py does
        plugin_helpers.load(
            namespace='wazo_setupd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'spec': SPEC,
                'status_aggregator': status_aggregator,
                'stopper': stopper,
            },
        )

    def _get_flask_api_paths(self):
        """Extract API paths from Flask app routes.

        Returns paths relative to the API prefix (e.g., '/setup' not '/1.0/setup').
        """
        api_paths = set()
        api_prefix = '/1.0'

        for rule in app.url_map.iter_rules():
            path = rule.rule
            # Skip excluded paths
            if path in EXCLUDED_PATHS:
                continue
            # Only include paths under the API prefix
            if path.startswith(api_prefix):
                # Strip the version prefix to get the API path
                api_path = path[len(api_prefix) :]
                if api_path:  # Skip empty path (the prefix itself)
                    api_paths.add(api_path)

        return api_paths

    def _get_spec_paths(self):
        """Extract documented paths from the OpenAPI spec."""
        spec_dict = SPEC.to_dict()
        return set(spec_dict.get('paths', {}).keys())

    def test_all_flask_endpoints_documented_in_spec(self):
        """Every Flask API endpoint must be documented in the OpenAPI spec.

        This test ensures that when a new endpoint is added to the Flask app,
        it must also be registered in the OpenAPI spec via the plugin's
        register_spec() method.
        """
        flask_paths = self._get_flask_api_paths()
        spec_paths = self._get_spec_paths()

        undocumented = flask_paths - spec_paths

        assert (
            not undocumented
        ), f"Flask endpoints {undocumented} missing from openapi spec"
