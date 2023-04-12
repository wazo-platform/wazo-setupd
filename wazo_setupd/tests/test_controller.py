# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
import signal
from unittest import TestCase
from unittest.mock import Mock

from ..controller import _signal_handler


class TestController(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sigterm_handler(self):
        controller_mock = Mock()
        _signal_handler(controller_mock, signal.SIGTERM, Mock())
        controller_mock.stop.assert_called_once_with(reason="SIGTERM")
