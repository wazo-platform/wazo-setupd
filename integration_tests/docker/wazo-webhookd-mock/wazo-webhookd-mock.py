#!/usr/bin/env python3
# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json
import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request, Response

from xivo.config_helper import read_config_file_hierarchy

logging.basicConfig(level=logging.DEBUG)

_EMPTY_RESPONSES = {
    'config': {},
    'subscriptions': {},
}

app = Flask(__name__)
logger = logging.getLogger('wazo-webhookd-mock')

_requests: list[dict[str, dict]] = []
_responses: dict[str, dict] = {}

port = int(sys.argv[1])
try:
    url_prefix = sys.argv[2]
except IndexError:
    url_prefix = ''


def _reset() -> None:
    global _requests
    global _responses
    _requests = []
    _responses = dict(_EMPTY_RESPONSES)


def load_config():
    return read_config_file_hierarchy(
        {
            'config_file': '/etc/wazo-webhookd/config.yml',
            'extra_config_files': '/etc/wazo-webhookd/conf.d',
        }
    )


@app.errorhandler(500)
def handle_generic(e: Exception) -> Response:
    logger.error(f'Exception: {e}')
    return jsonify({'error': str(e)})


@app.before_request
def log_request() -> None:
    if not request.path.startswith('/_'):
        path = request.path
        log = {
            'method': request.method,
            'path': path,
            'query': dict(request.args.items(multi=True)),
            'body': request.data.decode('utf-8'),
            'json': request.json
            if request.content_type == 'application/json'
            else None,
            'headers': dict(request.headers),
        }
        _requests.append(log)


@app.after_request
def print_request_response(response: Response) -> Response:
    logger.debug(
        'request: %s',
        {
            'method': request.method,
            'path': request.path,
            'query': dict(request.args.items(multi=True)),
            'body': request.data.decode('utf-8'),
            'headers': dict(request.headers),
        },
    )
    logger.debug('response: %s', {'body': response.data})
    return response


@app.route('/_requests', methods=['GET'])
def list_requests() -> Response:
    return jsonify(requests=_requests)


@app.route('/_reset', methods=['POST'])
def reset() -> tuple[str, int]:
    _reset()
    return '', 204


@app.route('/_set_response', methods=['POST'])
def set_response() -> tuple[str, int]:
    global _responses
    request_body = json.loads(request.data)
    set_response = request_body['response']
    set_response_body = request_body['content']
    _responses[set_response] = set_response_body
    return '', 204


@app.route(f'{url_prefix}/1.0/config')
def config() -> Response:
    result = _responses['config'] or dict(load_config())
    return jsonify(result)


@app.route(f'{url_prefix}/1.0/subscriptions', methods=['POST'])
def subscriptions() -> Response:
    return jsonify(_responses['subscriptions'])


if __name__ == '__main__':
    _reset()
    app.run(host='0.0.0.0', port=port, debug=True)
