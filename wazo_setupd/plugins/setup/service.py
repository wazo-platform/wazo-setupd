# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from requests import HTTPError
from xivo_auth_client import Client as AuthClient

from .exceptions import SetupError


class SetupService:

    def setup(self, setup_infos):
        nestbox_token = self.get_nestbox_token(setup_infos['nestbox_host'],
                                               setup_infos['nestbox_port'],
                                               setup_infos['nestbox_verify_certificate'],
                                               setup_infos['nestbox_service_id'],
                                               setup_infos['nestbox_service_key'])

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
