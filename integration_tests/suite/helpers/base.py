# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from contextlib import contextmanager
from wazo_setupd_client import Client as SetupdClient
from xivo_test_helpers import until
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_test_helpers.auth import AuthClient
from .confd import ConfdMockClient
from .deployd import DeploydMockClient
from .sysconfd import SysconfdMockClient
from .wait_strategy import WaitStrategy
from .webhookd import WebhookdMockClient

VALID_TOKEN = 'valid-token'


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
    )
    service = 'setupd'
    wait_strategy = WaitStrategy()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setupd = cls.make_setupd(VALID_TOKEN)
        cls.wait_strategy.wait(setupd)

    @classmethod
    def make_setupd(cls, token):
        return SetupdClient(
            '127.0.0.1',
            cls.service_port(9302, 'setupd'),
            prefix=None,
            https=False,
            token=token,
        )

    def make_auth(self):
        return AuthClient('127.0.0.1', self.service_port(9497, 'nestbox-auth'))

    def make_confd(self):
        return ConfdMockClient('127.0.0.1', self.service_port(9486, 'confd'))

    def make_deployd(self):
        return DeploydMockClient(
            '127.0.0.1', self.service_port(9800, 'nestbox-deployd')
        )

    def make_sysconfd(self):
        return SysconfdMockClient('127.0.0.1', self.service_port(8668, 'sysconfd'))

    def make_webhookd(self):
        return WebhookdMockClient('127.0.0.1', self.service_port(9300, 'webhookd'))

    @contextmanager
    def auth_stopped(self):
        self.stop_service('auth')
        yield
        self.start_service('auth')
        auth = self.make_auth()
        until.true(auth.is_up, tries=5, message='wazo-auth did not come back up')
