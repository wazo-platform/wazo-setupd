# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import Mock

from ..controller import _sigterm_handler


class Testclassname(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sigterm_handler(self):
        _sigterm_handler(Mock(), Mock(), Mock())
