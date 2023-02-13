# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    assert_that,
    calling,
    empty,
    has_entries,
    has_item,
    has_items,
    has_properties,
    not_,
)
from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import (
    BaseIntegrationTest,
    VALID_TOKEN,
)
from .helpers.wait_strategy import (
    NoWaitStrategy,
    SetupdEverythingOkWaitStrategy,
)

from wazo_setupd_client.exceptions import SetupdError


class TestSetupErrors(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def test_setup_empty(self):
        setupd = self.make_setupd(VALID_TOKEN)

        assert_that(
            calling(setupd.setup.create).with_args({}),
            raises(SetupdError).matching(has_properties(status_code=400)),
        )

    def test_setup_missing_nestbox(self):
        setupd = self.make_setupd(VALID_TOKEN)
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'nestbox_host': 'nestbox',
        }

        assert_that(
            calling(setupd.setup.create).with_args(body),
            raises(SetupdError).matching(has_properties(status_code=400)),
        )

    def test_setup_invalid_credentials(self):
        setupd = self.make_setupd(VALID_TOKEN)
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'nestbox_host': 'nestbox',
            'nestbox_port': 443,
            'nestbox_verify_certificate': False,
            'nestbox_service_id': 'test',
            'nestbox_service_key': 'foobar',
            'nestbox_instance_name': 'my-wazo',
            'nestbox_engine_host': 'wazo.example.com',
            'nestbox_engine_port': 443,
        }

        assert_that(
            calling(setupd.setup.create).with_args(body),
            raises(SetupdError).matching(
                has_properties(
                    status_code=500,
                    error_id='setup-token-failed',
                )
            ),
        )

    def test_setup_when_more_than_three_nameservers(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover(
            {"nameservers": ['10.2.2.2', '10.2.2.3', '10.2.2.4', '10.2.2.5']}
        )
        confd.set_wizard({'configured': False})
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_license': True,
        }

        assert_that(
            calling(setupd.setup.create).with_args(body),
            raises(SetupdError).matching(
                has_properties(
                    status_code=500,
                    error_id='setup-nameservers-failed',
                )
            ),
        )


class TestSetupValid(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = SetupdEverythingOkWaitStrategy()

    def setUp(self):
        super().setUp()

        deployd = self.make_deployd()
        deployd.reset()

        self.restart_service('setupd')  # avoid self-stop after test
        setupd = self.make_setupd(VALID_TOKEN)
        self.wait_strategy.wait(setupd)

    def test_setup_valid(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover(
            {
                "timezone": 'America/Montreal',
                "hostname": 'wazo-engine',
                "domain": 'example.com',
                'interfaces': [
                    {
                        'interface': 'my-interface',
                        'ip_address': '10.1.1.1',
                        'netmask': '255.0.0.0',
                    }
                ],
                'gateways': [{'gateway': '10.254.254.254'}],
                "nameservers": ['10.2.2.2'],
            }
        )
        confd.set_wizard({'configured': False})
        confd.set_rtp({'options': {'rtpstart': '10000', 'rtpend': '20000'}})
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        deployd.set_post_instance({'uuid': instance_uuid})
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'engine_rtp_icesupport': True,
            'engine_rtp_stunaddr': 'stun.example.com:3478',
            'nestbox_host': 'nestbox',
            'nestbox_port': 443,
            'nestbox_verify_certificate': False,
            'nestbox_service_id': 'nestbox-user',
            'nestbox_service_key': 'secret',
            'nestbox_instance_name': 'my-wazo',
            'nestbox_engine_host': 'wazo.example.com',
            'nestbox_engine_port': 6666,
        }

        setupd.setup.create(body)
        self.synchronize_setup_config_files()

        assert_that(
            confd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='POST',
                        path='/1.1/wizard',
                        json=has_entries(
                            network=has_entries(
                                hostname='wazo-engine',
                                domain='example.com',
                            )
                        ),
                    )
                )
            ),
        )
        assert_that(
            confd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='PUT',
                        path='/1.1/asterisk/rtp/general',
                        json=has_entries(
                            options=has_entries(
                                rtpstart='10000',
                                rtpend='20000',
                                icesupport='yes',
                                stunaddr='stun.example.com:3478',
                            )
                        ),
                    )
                )
            ),
        )
        assert_that(
            deployd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='POST',
                        path='/0.1/instances',
                        json=has_entries(
                            config={},
                            name='my-wazo',
                            password='secret',
                            private_host='10.1.1.1',
                            private_port=6666,
                            public_host='wazo.example.com',
                            public_port=6666,
                            service_id=1,
                            username='root',
                        ),
                    )
                )
            ),
        )
        webhookd = self.make_webhookd()
        assert_that(
            webhookd.get_config().json(),
            has_entries(
                nestbox=has_entries(
                    instance_uuid=instance_uuid,
                    auth={
                        'host': 'nestbox',
                        'port': 443,
                        'prefix': '/api/auth',
                        'service_id': 'nestbox-user',
                        'service_key': 'secret',
                        'verify_certificate': False,
                    },
                )
            ),
        )
        sysconfd = self.make_sysconfd()
        assert_that(
            sysconfd.requests().json(),
            has_entries(
                requests=has_items(
                    has_entries(
                        method='POST',
                        path='/services',
                        json={'wazo-auth': 'restart', 'wazo-webhookd': 'restart'},
                    )
                )
            ),
        )

    def test_setup_valid_already_registered_on_nestbox(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover(
            {
                "timezone": 'America/Montreal',
                "hostname": 'wazo-engine',
                "domain": 'example.com',
                'interfaces': [
                    {
                        'interface': 'my-interface',
                        'ip_address': '10.1.1.1',
                        'netmask': '255.0.0.0',
                    }
                ],
                'gateways': [{'gateway': '10.254.254.254'}],
                "nameservers": ['10.2.2.2'],
            }
        )
        confd.set_wizard({'configured': False})
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'engine_instance_uuid': instance_uuid,
            'nestbox_host': 'nestbox',
            'nestbox_port': 443,
            'nestbox_verify_certificate': False,
            'nestbox_service_id': 'nestbox-user',
            'nestbox_service_key': 'secret',
            'nestbox_instance_name': 'my-wazo',
            'nestbox_engine_host': 'wazo.example.com',
            'nestbox_engine_port': 6666,
        }

        setupd.setup.create(body)
        self.synchronize_setup_config_files()

        assert_that(
            confd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='POST',
                        path='/1.1/wizard',
                        json=has_entries(
                            network=has_entries(
                                hostname='wazo-engine',
                                domain='example.com',
                            )
                        ),
                    )
                )
            ),
        )
        assert_that(
            deployd.requests().json(),
            not_(
                has_entries(
                    requests=has_item(
                        has_entries(
                            method='POST',
                            path='/0.1/instances',
                        )
                    )
                )
            ),
        )
        assert_that(
            deployd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='PUT',
                        path='/0.1/instances/{}'.format(instance_uuid),
                        json=has_entries(installed=True),
                    )
                )
            ),
        )
        webhookd = self.make_webhookd()
        assert_that(
            webhookd.get_config().json(),
            has_entries(
                nestbox=has_entries(
                    instance_uuid=instance_uuid,
                    auth={
                        'host': 'nestbox',
                        'port': 443,
                        'prefix': '/api/auth',
                        'service_id': 'nestbox-user',
                        'service_key': 'secret',
                        'verify_certificate': False,
                    },
                )
            ),
        )
        sysconfd = self.make_sysconfd()
        assert_that(
            sysconfd.requests().json(),
            has_entries(
                requests=has_items(
                    has_entries(
                        method='POST',
                        path='/services',
                        json={'wazo-auth': 'restart', 'wazo-webhookd': 'restart'},
                    ),
                )
            ),
        )


class TestSetupValidNoNestbox(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def test_setup_valid_without_nestbox(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover(
            {
                "timezone": 'America/Montreal',
                "hostname": 'wazo-engine',
                "domain": 'example.com',
                'interfaces': [
                    {
                        'interface': 'my-interface',
                        'ip_address': '10.1.1.1',
                        'netmask': '255.0.0.0',
                    }
                ],
                'gateways': [{'gateway': '10.254.254.254'}],
                "nameservers": ['10.2.2.2'],
            }
        )
        confd.set_wizard({'configured': False})
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        deployd.set_post_instance({'uuid': instance_uuid})
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_license': True,
        }

        setupd.setup.create(body)
        self.synchronize_setup_config_files()

        assert_that(
            confd.requests().json(),
            has_entries(
                requests=has_item(
                    has_entries(
                        method='POST',
                        path='/1.1/wizard',
                        json=has_entries(
                            network=has_entries(
                                hostname='wazo-engine',
                                domain='example.com',
                            )
                        ),
                    )
                )
            ),
        )
        assert_that(deployd.requests().json(), has_entries(requests=empty()))
        webhookd = self.make_webhookd()
        assert_that(webhookd.get_config().json(), empty())


class TestSetupSelfStop(BaseIntegrationTest):
    asset = 'short-self-stop'
    wait_strategy = NoWaitStrategy()

    def test_setup_valid_stops(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover(
            {
                "timezone": 'America/Montreal',
                "hostname": 'wazo-engine',
                "domain": 'example.com',
                'interfaces': [
                    {
                        'interface': 'my-interface',
                        'ip_address': '10.1.1.1',
                        'netmask': '255.0.0.0',
                    }
                ],
                'gateways': [{'gateway': '10.254.254.254'}],
                "nameservers": ['10.2.2.2'],
            }
        )
        confd.set_wizard({'configured': False})
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        deployd.set_post_instance({'uuid': instance_uuid})
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'nestbox_host': 'nestbox',
            'nestbox_port': 443,
            'nestbox_verify_certificate': False,
            'nestbox_service_id': 'nestbox-user',
            'nestbox_service_key': 'secret',
            'nestbox_instance_name': 'my-wazo',
            'nestbox_engine_host': 'wazo.example.com',
            'nestbox_engine_port': 6666,
        }

        setupd.setup.create(body)

        def setupd_is_stopped():
            return not self.service_status('setupd')['State']['Running']

        until.true(setupd_is_stopped, timeout=10)


class TestSetupNotSelfStop(BaseIntegrationTest):
    asset = 'short-self-stop'
    wait_strategy = NoWaitStrategy()

    def test_setup_invalid_does_not_stop(self):
        setupd = self.make_setupd(VALID_TOKEN)
        body = {
            'engine_language': 'en_US',
            'engine_password': 'secret',
            'engine_internal_address': '10.1.1.1',
            'engine_license': True,
            'nestbox_host': 'nestbox',
            'nestbox_port': 443,
            'nestbox_verify_certificate': False,
            'nestbox_service_id': 'test',
            'nestbox_service_key': 'foobar',
            'nestbox_instance_name': 'my-wazo',
            'nestbox_engine_host': 'wazo.example.com',
            'nestbox_engine_port': 443,
        }

        assert_that(
            calling(setupd.setup.create).with_args(body),
            raises(SetupdError).matching(
                has_properties(
                    status_code=500,
                    error_id='setup-token-failed',
                )
            ),
        )

        def setupd_is_stopped():
            return not self.service_status('setupd')['State']['Running']

        try:
            until.true(setupd_is_stopped, timeout=10)
        except until.NoMoreTries:
            return
        else:
            raise AssertionError('wazo-setupd stopped after failed setup')
