#!/usr/bin/env python3
# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json
import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request, Response

logging.basicConfig(level=logging.DEBUG)

_EMPTY_RESPONSES = {
    'instances': {},
    'post_instance': {},
}

app = Flask(__name__)
logger = logging.getLogger('wazo-deployd-mock')

_requests: list[dict[str, dict]] = []
_responses: dict[str, dict] = {}

port = int(sys.argv[1])
try:
    url_prefix = sys.argv[2]
except IndexError:
    url_prefix = ''


@app.errorhandler(500)
def handle_generic(e: Exception) -> Response:
    logger.error(f'Exception: {e}')
    return jsonify({'error': str(e)})


def _reset() -> None:
    global _requests
    global _responses
    _requests = []
    _responses = dict(_EMPTY_RESPONSES)


@app.before_request
def log_request() -> None:
    if not request.path.startswith('/_'):
        path = request.path
        log = {
            'method': request.method,
            'path': path,
            'query': dict(request.args.items(multi=True)),
            'body': request.data.decode('utf-8'),
            'json': request.json,
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


@app.route(f'{url_prefix}/0.1/instances', methods=['POST'])
def post_instance() -> Response:
    return jsonify(_responses['post_instance'])


@app.route(f'{url_prefix}/0.1/instances/<uuid:instance_uuid>', methods=['PUT'])
def put_instance(instance_uuid) -> Response:
    return jsonify(request.json)


@app.route(f'{url_prefix}/0.1/instances')
def instances() -> Response:
    return jsonify(_responses['instances'])


if __name__ == '__main__':
    _reset()

    context = (
        '/usr/local/share/ssl/deployd/server.crt',
        '/usr/local/share/ssl/deployd/server.key',
    )
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=True)
