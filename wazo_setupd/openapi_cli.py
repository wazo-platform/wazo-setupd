# Copyright 2025-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

"""CLI tool to generate and dump the OpenAPI spec to stdout."""

import argparse
import importlib.metadata
import json
import sys

import yaml
from apispec import APISpec

from wazo_setupd.openapi import SPEC, make_server_url


def register_plugins(spec: APISpec) -> None:
    """Register plugin specs (normally done at plugin load time)."""
    # use importlib to scan namespaces for plugins
    for plugin in importlib.metadata.entry_points(group='wazo_setupd.plugins'):
        plugin_klass = plugin.load()
        plugin_obj = plugin_klass()
        if hasattr(plugin_obj, 'register_spec'):
            plugin_obj.register_spec(spec)


def main():
    parser = argparse.ArgumentParser(
        description='Generate OpenAPI specification for wazo-setupd'
    )
    parser.add_argument(
        '-f',
        '--format',
        choices=['yaml', 'json'],
        default='yaml',
        help='Output format (default: yaml)',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default=None,
        help='Output file (default: stdout)',
    )
    parser.add_argument(
        '--base-path',
        type=str,
        default=None,
        help='Base path prefix for server URL (e.g. /api/setupd)',
    )
    parser.add_argument(
        '--scheme',
        type=str,
        default='http',
        help='scheme server URL (e.g. https)',
    )

    args = parser.parse_args()

    register_plugins(SPEC)

    if args.base_path:
        SPEC.options['servers'] = [make_server_url(args.base_path, scheme=args.scheme)]

    spec_dict = SPEC.to_dict()
    if args.format == 'json':
        output = json.dumps(spec_dict, indent=2)
    else:
        output = yaml.dump(spec_dict, default_flow_style=False)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
