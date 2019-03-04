# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests
import yaml

from requests import HTTPError
from xivo_auth_client import Client as AuthClient
from xivo_confd_client import Client as ConfdClient

from .exceptions import SetupError

logger = logging.getLogger(__name__)

ENGINE_SERVICE_ID = 1


class SetupService:

    def __init__(self, config, stopper):
        self._confd_config = config['confd']
        self._sysconfd_config = config['sysconfd']
        self._stopper = stopper

    def setup(self, setup_infos):
        nestbox_registration_enabled = 'nestbox_host' in setup_infos

        if nestbox_registration_enabled:
            self.setup_with_nestbox(setup_infos)
        else:
            self.setup_without_nestbox(setup_infos)

        self.plan_setupd_stop()

    def setup_with_nestbox(self, setup_infos):
        # This step serves as authentication. It must be the first step.
        nestbox_token = self.get_nestbox_token(
            setup_infos['nestbox_host'],
            setup_infos['nestbox_port'],
            setup_infos['nestbox_verify_certificate'],
            setup_infos['nestbox_service_id'],
            setup_infos['nestbox_service_key'],
        )

        self.post_confd_wizard(
            setup_infos['engine_entity_name'],
            setup_infos['engine_language'],
            setup_infos['engine_number_start'],
            setup_infos['engine_number_end'],
            setup_infos['engine_password'],
            setup_infos['engine_license'],
        )

        instance_uuid = self.register_instance(
            nestbox_token,
            setup_infos['nestbox_host'],
            setup_infos['nestbox_port'],
            setup_infos['nestbox_verify_certificate'],
            setup_infos['nestbox_instance_name'],
            setup_infos['nestbox_engine_host'],
            setup_infos['nestbox_engine_port'],
            setup_infos['engine_internal_address'],
            setup_infos['engine_password'],
        )
        self.inject_nestbox_config(
            setup_infos['nestbox_host'],
            setup_infos['nestbox_port'],
            setup_infos['nestbox_verify_certificate'],
            setup_infos['nestbox_service_id'],
            setup_infos['nestbox_service_key'],
            instance_uuid,
        )

    def setup_without_nestbox(self, setup_infos):
        self.remove_nestbox_dependencies()
        self.post_confd_wizard(
            setup_infos['engine_entity_name'],
            setup_infos['engine_language'],
            setup_infos['engine_number_start'],
            setup_infos['engine_number_end'],
            setup_infos['engine_password'],
            setup_infos['engine_license'],
        )

    def get_nestbox_token(self, nestbox_host, nestbox_port, nestbox_verify_certificate, service_id, service_key):
        auth = AuthClient(
            nestbox_host,
            port=nestbox_port,
            username=service_id,
            password=service_key,
            prefix="/api/auth",
            verify_certificate=nestbox_verify_certificate,
        )
        try:
            token_data = auth.token.new('wazo_user', expiration=600)
        except HTTPError:
            raise SetupError(
                message='Failed to create authorization token',
                error_id='setup-token-failed',
                details={
                    'auth_host': nestbox_host,
                    'auth_port': nestbox_port,
                    'service_key': service_id,
                }
            )
        return token_data['token']

    def post_confd_wizard(self, entity_name, language, number_start, number_end, password, license_accepted):
        c = ConfdClient(**self._confd_config)

        if c.wizard.get()['configured']:
            logger.info("Wizard already configured...")
            return

        discover = c.wizard.discover()

        if not discover.get('domain'):
            discover['domain'] = 'localdomain'

        wizard = {
            "admin_password": password,
            "license": license_accepted,
            "timezone": discover['timezone'],
            "language": language,
            "entity_name": entity_name,
            "network": {
                "hostname": discover['hostname'],
                "domain": discover['domain'],
                "interface": discover['interfaces'][0]['interface'],
                "ip_address": discover['interfaces'][0]['ip_address'],
                "netmask": discover['interfaces'][0]['netmask'],
                "gateway": discover['gateways'][0]['gateway'],
                "nameservers": discover['nameservers']
            },
            "context_incall": {
                "display_name": "Incalls",
                "did_length": 4
            },
            "context_internal": {
                "display_name": "Default",
                "number_start": number_start,
                "number_end": number_end
            },
            "context_outcall": {
                "display_name": "Outcalls"
            }
        }

        c.wizard.create(wizard)

    def remove_nestbox_dependencies(self):
        url = "http://{host}:{port}/remove_nestbox_dependencies".format(
            host=self._sysconfd_config['host'],
            port=self._sysconfd_config['port'],
        )
        try:
            response = requests.get(url)
        except requests.RequestsException as e:
            raise SetupError('xivo-sysconfd connection error',
                             error_id='xivo-sysconfd-connection-error',
                             details={'original_error': e})
        if response.status_code != 200:
            raise SetupError('xivo-sysconfd failure',
                             error_id='xivo-sysconfd-failure',
                             details={'sysconfd-error': response.text})

    def register_instance(self,
                          token,
                          nestbox_host,
                          nestbox_port,
                          nestbox_verify_certificate,
                          nestbox_instance_name,
                          nestbox_engine_host,
                          nestbox_engine_port,
                          engine_internal_address,
                          engine_password):
        # wazo-deployd-client was just installed by xivo-sysconfd, at the
        # request of wazo-setupd, thus we need a lazy import
        from wazo_deployd_client import Client as DeploydClient

        deployd = DeploydClient(
            nestbox_host,
            port=nestbox_port,
            token=token,
            prefix="/api/deployd",
            verify_certificate=nestbox_verify_certificate,
        )
        instance_data = {
            "remote_host": nestbox_engine_host,
            "https_port": nestbox_engine_port,
            "name": nestbox_instance_name,
            "interface_ip": engine_internal_address,
            "username": "root",
            "password": engine_password,
            "config": {},
            "service_id": ENGINE_SERVICE_ID,
        }
        instance = deployd.instances.register(instance_data)
        return instance['uuid']

    def inject_nestbox_config(self,
                              nestbox_host,
                              nestbox_port,
                              nestbox_verify_certificate,
                              nestbox_service_id,
                              nestbox_service_key,
                              instance_uuid):
        nestbox_config_file = "/etc/wazo-nestbox-plugin/conf.d/50-wazo-plugin-nestbox.yml"
        config = {
            "nestbox": {
                "instance_uuid": instance_uuid,
                "auth": {
                    "host": nestbox_host,
                    "port": nestbox_port,
                    "prefix": "/api/auth",
                    "service_id": nestbox_service_id,
                    "service_key": nestbox_service_key,
                    "verify_certificate": nestbox_verify_certificate,
                },
                "confd": {
                    "host": nestbox_host,
                    "port": nestbox_port,
                    "prefix": "/api/confd",
                    "verify_certificate": nestbox_verify_certificate,
                }
            }
        }

        with open(nestbox_config_file, 'w') as _file:
            yaml.dump(config, _file, default_flow_style=False)

        session = requests.Session()
        session.trust_env = False
        url = 'http://{host}:{port}/services'.format(
            host=self._sysconfd_config['host'],
            port=self._sysconfd_config['port'],
        )
        data = {'wazo-webhookd': 'restart'}
        try:
            response = session.post(url, json=data)
        except requests.RequestsException as e:
            raise SetupError('xivo-sysconfd connection error',
                             error_id='xivo-sysconfd-connection-error',
                             details={'original_error': e})
        if response.status_code != 200:
            raise SetupError('xivo-sysconfd failure',
                             error_id='xivo-sysconfd-failure',
                             details={'sysconfd-error': response.text})

    def plan_setupd_stop(self):
        self._stopper.trigger()
