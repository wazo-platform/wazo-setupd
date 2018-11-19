# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import threading

logger = logging.getLogger(__name__)


class Stopper:

    def __init__(self, stop_delay, controller):
        self._stop_delay = stop_delay
        self._event = threading.Event()
        self._cancel_event = threading.Event()
        self._controller = controller

    def wait(self):
        logger.debug('stopper waiting...')
        self._event.wait()
        logger.debug('stopper stopped waiting. starting timer...')
        if self._cancel_event.wait(timeout=self._stop_delay):
            logger.debug('stopper interrupted by cancel')
            return
        logger.debug('stopper triggering daemon stop')
        self._controller.stop(reason='self-stopper triggered')

    def trigger(self):
        logger.debug('stopper triggered')
        self._event.set()

    def cancel(self):
        logger.debug('stopper cancelled')
        self._cancel_event.set()
        self._event.set()
