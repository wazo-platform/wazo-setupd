# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
import logging
import subprocess
import yaml

from requests import HTTPError
from xivo_auth_client import Client as AuthClient
from xivo_confd_client import Client as ConfdClient
from wazo_deployd_client import Client as DeploydClient

from .exceptions import SetupError

logger = logging.getLogger(__name__)


class SetupService:

    def setup(self, setup_infos):
        # This step serves as authentication. It must be the first step.
        nestbox_token = self.get_nestbox_token(setup_infos['nestbox_host'],
                                               setup_infos['nestbox_port'],
                                               setup_infos['nestbox_verify_certificate'],
                                               setup_infos['nestbox_service_id'],
                                               setup_infos['nestbox_service_key'])
        self.post_confd_wizard(setup_infos['engine_entity_name'],
                               setup_infos['engine_language'],
                               setup_infos['engine_number_start'],
                               setup_infos['engine_number_end'],
                               setup_infos['engine_password'])
        instance_uuid = self.register_instance(nestbox_token,
                                               setup_infos['nestbox_host'],
                                               setup_infos['nestbox_port'],
                                               setup_infos['nestbox_verify_certificate'],
                                               setup_infos['nestbox_instance_name'],
                                               setup_infos['nestbox_engine_host'],
                                               setup_infos['nestbox_engine_port'],
                                               setup_infos['engine_internal_address'],
                                               setup_infos['engine_password'])
        self.inject_nestbox_config(setup_infos['nestbox_host'],
                                   setup_infos['nestbox_port'],
                                   setup_infos['nestbox_service_id'],
                                   setup_infos['nestbox_service_key'],
                                   instance_uuid)

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

    def post_confd_wizard(self, entity_name, language, number_start, number_end, password):
        c = ConfdClient('localhost',
                        port=9486,
                        https=True,
                        verify_certificate='/usr/share/xivo-certs/server.crt')

        if c.wizard.get()['configured']:
            logger.info("Wizard already configured...")
            return

        discover = c.wizard.discover()

        if not discover.get('domain'):
            discover['domain'] = 'localdomain'

        wizard = {
            "admin_password": password,
            "license": True,
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
        deployd = DeploydClient(nestbox_host,
                                port=nestbox_port,
                                token=token,
                                prefix="/api/deployd",
                                verify_certificate=nestbox_verify_certificate)
        instance_data = {
            "remote_host": nestbox_engine_host,
            "https_port": nestbox_engine_port,
            "name": nestbox_instance_name,
            "interface_ip": engine_internal_address,
            "username": "root",
            "password": engine_password,
            "config": {},
            "service_id": 1,
        }
        instance = deployd.instances.register(instance_data)
        return instance['uuid']

    def inject_nestbox_config(self,
                              nestbox_host,
                              nestbox_port,
                              nestbox_service_id,
                              nestbox_service_key,
                              instance_uuid):
        nestbox_config_file = "/etc/wazo-nestbox-plugin/conf.d/50-wazo-plugin-nestbox.yml"
        webhookd_config_file = "/etc/wazo-webhookd/conf.d/50-wazo-plugin-nestbox.yml"
        config = {
            "nestbox": {
                "instance_uuid": instance_uuid,
                "auth": {
                    "host": nestbox_host,
                    "port": nestbox_port,
                    "prefix": "/api/auth",
                    "service_id": nestbox_service_id,
                    "service_key": nestbox_service_key,
                    "verify_certificate": False
                },
                "confd": {
                    "host": nestbox_host,
                    "port": nestbox_port,
                    "prefix": "/api/confd",
                    "verify_certificate": False
                }
            }
        }

        with open(nestbox_config_file, 'w') as _file:
            yaml.dump(config, _file, default_flow_style=False)

        try:
            os.symlink(nestbox_config_file, webhookd_config_file)
        except FileExistsError:
            pass

        subprocess.run(["systemctl", "restart", "wazo-webhookd"])
