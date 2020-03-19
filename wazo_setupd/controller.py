# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal
import threading

from functools import partial
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from .http_server import api, CoreRestApi
from .stopper import Stopper

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config):
        self._service_discovery_args = [
            'wazo-setupd',
            config.get('uuid'),
            config['consul'],
            config['service_discovery'],
            config['bus'],
            lambda: True,
        ]
        self.rest_api = CoreRestApi(config)
        self.stopper = Stopper(config['self_stop_delay'], self)
        plugin_helpers.load(
            namespace='wazo_setupd.plugins',
            names=config['enabled_plugins'],
            dependencies={'api': api, 'config': config, 'stopper': self.stopper},
        )
        self.stopper_thread = threading.Thread(target=self.stopper.wait)

    def run(self):
        logger.info('wazo-setupd starting...')
        signal.signal(signal.SIGTERM, partial(_sigterm_handler, self))
        self.stopper_thread.start()
        try:
            with ServiceCatalogRegistration(*self._service_discovery_args):
                self.rest_api.run()

        finally:
            logger.info('wazo-setupd stopping...')
            logger.debug('joining stopper thread')
            self.stopper.cancel()
            self.stopper_thread.join()

    def stop(self, reason):
        logger.warning('Stopping wazo-setupd: %s', reason)
        self.rest_api.stop()


def _sigterm_handler(controller, signum, frame):
    controller.stop(reason='SIGTERM')
