# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import Mock, patch, sentinel as s
from contextlib import contextmanager

from .. import services
from ..services import SetupService


class TestSetupService(TestCase):
    def setUp(self):
        self.auth_config = {}
        self.confd_config = {}
        self.sysconfd_config = {}
        self.config = {
            'auth': self.auth_config,
            'confd': self.confd_config,
            'sysconfd': self.sysconfd_config,
        }
        self.stopper = Mock()

        self.service = SetupService(self.config, self.stopper,)

    def test_setup_rtp(self):
        with self.confd_mock() as client:
            self.service.setup_rtp(s.password, False, None)
            client.rtp_general.update.assert_not_called()

        with self.confd_mock() as client:
            with self.get_engine_token_mock():
                rtp_config = {
                    'rtpstart': 10000,
                    'rtpend': 20000,
                }
                client.rtp_general.get.return_value = {'options': dict(rtp_config)}
                self.service.setup_rtp(s.password, False, 'myserver')
                client.rtp_general.update.assert_called_once_with(
                    {'options': {'stunaddr': 'myserver', **rtp_config}}
                )

        with self.confd_mock() as client:
            with self.get_engine_token_mock():
                rtp_config = {
                    'rtpstart': 10000,
                    'rtpend': 20000,
                }
                client.rtp_general.get.return_value = {'options': dict(rtp_config)}
                self.service.setup_rtp(s.password, True, 'myserver')
                client.rtp_general.update.assert_called_once_with(
                    {
                        'options': {
                            'icesupport': 'yes',
                            'stunaddr': 'myserver',
                            **rtp_config,
                        }
                    }
                )

    @contextmanager
    def get_engine_token_mock(self):
        with patch.object(self.service, 'get_engine_token') as token:
            yield token

    @contextmanager
    def confd_mock(self):
        with patch.object(services, 'ConfdClient') as factory:
            client = factory.return_value = Mock(name='confd_client')
            yield client
