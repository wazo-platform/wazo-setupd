# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import uuid

from hamcrest import (
    all_of,
    assert_that,
    calling,
    has_entries,
    has_entry,
    has_item,
    has_property,
)
from xivo_test_helpers import until
from xivo_test_helpers.hamcrest.raises import raises

from .helpers.base import BaseIntegrationTest
from .helpers.base import VALID_TOKEN
from .helpers.wait_strategy import NoWaitStrategy

from wazo_setupd_client.exceptions import SetupdError


class TestSetup(BaseIntegrationTest):

    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def test_setup_empty(self):
        setupd = self.make_setupd(VALID_TOKEN)

        assert_that(calling(setupd.setup.create).with_args({}),
                    raises(SetupdError).matching(has_property('status_code', 400)))

    def test_setup_invalid_credentials(self):
        setupd = self.make_setupd(VALID_TOKEN)
        body = {
            'engine_entity_name': 'Wazo',
            'engine_language': 'en_US',
            'engine_number_start': '1000',
            'engine_number_end': '1999',
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

        assert_that(calling(setupd.setup.create).with_args(body),
                    raises(SetupdError).matching(all_of(has_property('status_code', 500),
                                                        has_property('error_id', 'setup-token-failed'))))

    def test_setup_valid(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover({
            "timezone": 'America/Montreal',
            "hostname": 'wazo-engine',
            "domain": 'example.com',
            'interfaces': [
                {'interface': 'my-interface',
                 'ip_address': '10.1.1.1',
                 'netmask': '255.0.0.0'}
            ],
            'gateways': [
                {'gateway': '10.254.254.254'}
            ],
            "nameservers": ['10.2.2.2']
        })
        confd.set_wizard({
            'configured': False,
        })
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        deployd.set_post_instance({
            'uuid': instance_uuid,
        })
        body = {
            'engine_entity_name': 'Wazo',
            'engine_language': 'en_US',
            'engine_number_start': '1000',
            'engine_number_end': '1999',
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

        assert_that(confd.requests().json(), has_entry('requests', has_item(has_entries({
            'method': 'POST',
            'path': '/1.1/wizard',
            'json': has_entry('network', has_entries({
                'hostname': 'wazo-engine',
                'domain': 'example.com',
            }))
        }))))
        assert_that(deployd.requests().json(), has_entry('requests', has_item(has_entries({
            'method': 'POST',
            'path': '/0.1/instances',
            'json': {
                'config': {},
                'https_port': 6666,
                'interface_ip': '10.1.1.1',
                'name': 'my-wazo',
                'password': 'secret',
                'remote_host': 'wazo.example.com',
                'service_id': 1,
                'username': 'root'
            },
        }))))
        webhookd = self.make_webhookd()
        assert_that(webhookd.get_config().json(), has_entry('nestbox', has_entries({
           'instance_uuid': instance_uuid,
           'auth': {
               'host': 'nestbox',
               'port': 443,
               'prefix': '/api/auth',
               'service_id': 'nestbox-user',
               'service_key': 'secret',
               'verify_certificate': False
           },
        })))
        sysconfd = self.make_sysconfd()
        assert_that(sysconfd.requests().json(), has_entry('requests', has_item(has_entries({
            'method': 'POST',
            'path': '/services',
            'json': {
                'wazo-webhookd': 'restart',
            },
        }))))


class TestSetupSelfStop(BaseIntegrationTest):

    asset = 'short-self-stop'
    wait_strategy = NoWaitStrategy()

    def test_setup_valid_stops(self):
        setupd = self.make_setupd(VALID_TOKEN)
        confd = self.make_confd()
        confd.set_wizard_discover({
            "timezone": 'America/Montreal',
            "hostname": 'wazo-engine',
            "domain": 'example.com',
            'interfaces': [
                {'interface': 'my-interface',
                 'ip_address': '10.1.1.1',
                 'netmask': '255.0.0.0'}
            ],
            'gateways': [
                {'gateway': '10.254.254.254'}
            ],
            "nameservers": ['10.2.2.2']
        })
        confd.set_wizard({
            'configured': False,
        })
        instance_uuid = str(uuid.uuid4())
        deployd = self.make_deployd()
        deployd.set_post_instance({
            'uuid': instance_uuid,
        })
        body = {
            'engine_entity_name': 'Wazo',
            'engine_language': 'en_US',
            'engine_number_start': '1000',
            'engine_number_end': '1999',
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

        until.true(setupd_is_stopped, timeout=5)


class TestSetupNotSelfStop(BaseIntegrationTest):

    asset = 'short-self-stop'
    wait_strategy = NoWaitStrategy()

    def test_setup_invalid_does_not_stop(self):
        setupd = self.make_setupd(VALID_TOKEN)
        body = {
            'engine_entity_name': 'Wazo',
            'engine_language': 'en_US',
            'engine_number_start': '1000',
            'engine_number_end': '1999',
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

        assert_that(calling(setupd.setup.create).with_args(body),
                    raises(SetupdError).matching(all_of(has_property('status_code', 500),
                                                        has_property('error_id', 'setup-token-failed'))))

        def setupd_is_stopped():
            return not self.service_status('setupd')['State']['Running']

        try:
            until.true(setupd_is_stopped, timeout=5)
        except until.NoMoreTries:
            return
        else:
            raise AssertionError('wazo-setupd stopped after failed setup')
