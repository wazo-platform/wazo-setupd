# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from requests import HTTPError
from xivo_auth_client import Client as AuthClient
from xivo_confd_client import Client as Confd

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
        c = Confd('localhost', port=9486, https=True, verify_certificate='/usr/share/xivo-certs/server.crt')

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
