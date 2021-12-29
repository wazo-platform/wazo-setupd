# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from contextlib import contextmanager
from wazo_auth_client import Client as AuthClient
from wazo_setupd_client import Client as SetupdClient
from xivo.config_helper import parse_config_file
from wazo_test_helpers import until
from wazo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from wazo_test_helpers.auth import (
    AuthClient as MockAuthClient,
    MockCredentials,
    MockUserToken,
)
from .confd import ConfdMockClient
from .deployd import DeploydMockClient
from .sysconfd import SysconfdMockClient
from .wait_strategy import WaitStrategy
from .webhookd import WebhookdMockClient

VALID_TOKEN = 'valid-token-master-tenant'
VALID_SUB_TOKEN = 'valid-token-sub-tenant'

MASTER_TENANT = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeee10'
SUB_TENANT = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeee11'

WAZO_UUID = 'cd030e68-ace9-4ad4-bc4e-13c8dec67898'

MASTER_USER_UUID = '5f243438-a429-46a8-a992-baed872081e0'
SUB_USER_UUID = '5f243438-a429-46a8-a992-baed872081e1'


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
    )
    service = 'setupd'
    wait_strategy = WaitStrategy()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.asset not in ('documentation', 'short-self-stop'):
            cls.configure_wazo_auth()
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

    @classmethod
    def make_auth(cls):
        return AuthClient(
            '127.0.0.1', cls.service_port(9497, 'auth'), https=False, prefix=None
        )

    @classmethod
    def make_mock_auth(cls):
        return MockAuthClient('127.0.0.1', cls.service_port(9497, 'auth'))

    @classmethod
    def make_mock_nestbox_auth(cls):
        return MockAuthClient('127.0.0.1', cls.service_port(9497, 'nestbox-auth'))

    @classmethod
    def make_confd(cls):
        return ConfdMockClient('127.0.0.1', cls.service_port(9486, 'confd'))

    @classmethod
    def make_deployd(cls):
        return DeploydMockClient('127.0.0.1', cls.service_port(9800, 'nestbox-deployd'))

    @classmethod
    def make_sysconfd(cls):
        return SysconfdMockClient('127.0.0.1', cls.service_port(8668, 'sysconfd'))

    @classmethod
    def make_webhookd(cls):
        return WebhookdMockClient('127.0.0.1', cls.service_port(9300, 'webhookd'))

    @classmethod
    def configure_wazo_auth(cls):
        key_file = parse_config_file(
            os.path.join(cls.assets_root, 'keys', 'wazo-setupd-key.yml')
        )
        mock_auth = cls.make_mock_auth()
        mock_auth.set_valid_credentials(
            MockCredentials(key_file['service_id'], key_file['service_key']),
            VALID_TOKEN,
        )

        mock_auth.set_token(
            MockUserToken(
                VALID_TOKEN,
                MASTER_USER_UUID,
                WAZO_UUID,
                {'tenant_uuid': MASTER_TENANT, 'uuid': MASTER_USER_UUID},
            )
        )

        mock_auth.set_token(
            MockUserToken(
                VALID_SUB_TOKEN,
                SUB_USER_UUID,
                WAZO_UUID,
                {'tenant_uuid': SUB_TENANT, 'uuid': SUB_USER_UUID},
            )
        )

        mock_auth.set_tenants(
            {
                'uuid': MASTER_TENANT,
                'name': 'setupd-tests-master',
                'parent_uuid': MASTER_TENANT,
            },
            {
                'uuid': SUB_TENANT,
                'name': 'setupd-tests-sub',
                'parent_uuid': MASTER_TENANT,
            },
        )

    @contextmanager
    def auth_stopped(self):
        self.stop_service('auth')
        yield
        self.start_service('auth')
        auth = self.make_auth()
        until.true(auth.is_up, tries=5, message='wazo-auth did not come back up')

    def synchronize_setup_config_files(self):
        """This function is a workaround for this docker bug:
        https://github.com/moby/moby/issues/42119
        When this bug happens, network are not removed correctly, and volumes
        that should be removed after that are not removed. This makes the
        volumes to be shared across tests, causing failures.
        This function avoids the use of docker volumes altogether."""

        self.docker_copy_across_containers(
            'setupd',
            '/usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml',
            'webhookd',
            '/etc/wazo-webhookd/conf.d/50-wazo-plugin-nestbox.yml',
        )
        self.docker_copy_across_containers(
            'setupd',
            '/usr/share/wazo-setupd/50-wazo-plugin-nestbox.yml',
            'auth',
            '/etc/wazo-auth/conf.d/50-wazo-plugin-nestbox.yml',
        )
