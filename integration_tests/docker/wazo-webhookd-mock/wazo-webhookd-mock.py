#!/usr/bin/python
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request

from xivo.config_helper import read_config_file_hierarchy

logging.basicConfig(level=logging.DEBUG)

_EMPTY_RESPONSES = {
    'config': {},
    'subscriptions': {},
}

app = Flask(__name__)
logger = logging.getLogger('wazo-webhookd-mock')

_requests = []
_responses = {}

port = int(sys.argv[1])
try:
    url_prefix = sys.argv[2]
except IndexError:
    url_prefix = ''


def _reset():
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


@app.before_request
def log_request():
    if not request.path.startswith('/_'):
        path = request.path
        log = {
            'method': request.method,
            'path': path,
            'query': request.args.items(multi=True),
            'body': request.data,
            'json': request.json,
            'headers': dict(request.headers),
        }
        _requests.append(log)


@app.after_request
def print_request_response(response):
    logger.debug(
        'request: %s',
        {
            'method': request.method,
            'path': request.path,
            'query': request.args.items(multi=True),
            'body': request.data,
            'headers': dict(request.headers),
        },
    )
    logger.debug('response: %s', {'body': response.data,})
    return response


@app.route('/_requests', methods=['GET'])
def list_requests():
    return jsonify(requests=_requests)


@app.route('/_reset', methods=['POST'])
def reset():
    _reset()
    return '', 204


@app.route('/_set_response', methods=['POST'])
def set_response():
    global _responses
    request_body = json.loads(request.data)
    set_response = request_body['response']
    set_response_body = request_body['content']
    _responses[set_response] = set_response_body
    return '', 204


@app.route(url_prefix + '/1.0/config')
def config():
    result = _responses['config'] or dict(load_config())
    return jsonify(result)


@app.route(url_prefix + '/1.0/subscriptions', methods=['POST'])
def subscriptions():
    return jsonify(_responses['subscriptions'])


if __name__ == '__main__':
    _reset()

    context = (
        '/usr/local/share/ssl/webhookd/server.crt',
        '/usr/local/share/ssl/webhookd/server.key',
    )
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=True)
