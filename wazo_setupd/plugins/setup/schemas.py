# Copyright 2018-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import validates_schema
from marshmallow.exceptions import ValidationError
from xivo.mallow import fields, validate
from xivo.mallow_helpers import Schema


class SetupSchema(Schema):
    """Schema for Wazo Engine setup request."""

    engine_language = fields.String(
        required=True,
        validate=validate.OneOf(['en_US', 'fr_FR']),
        metadata={
            'description': 'The interface language for the Wazo Engine',
            'example': 'en_US',
        },
    )
    engine_password = fields.String(
        required=True,
        metadata={
            'description': 'Password of the first administrator "root" on the engine',
            'example': 'secret',
        },
    )
    engine_license = fields.Boolean(
        required=True,
        validate=validate.Equal(True),
        metadata={
            'description': 'Whether the GNU GPLv3 license is accepted',
            'example': True,
        },
    )
    engine_internal_address = fields.String(
        metadata={
            'description': 'IP address of the engine',
            'example': '192.168.1.100',
        },
    )
    engine_instance_uuid = fields.UUID(
        load_default=None,
        metadata={
            'description': (
                'The UUID identifying this instance on Nestbox. '
                'Should only be specified if the instance has already been registered '
                'on the specified Nestbox. Omitting this field for an instance that is '
                'already registered will create a duplicate entry on the Nestbox.'
            ),
            'example': '00000000-0000-4000-8000-000000000001',
        },
    )
    engine_rtp_icesupport = fields.Boolean(
        required=False,
        load_default=False,
        metadata={
            'description': (
                'Enable ICE support. This is required for WebRTC. '
                'A STUN server must be defined in the engine_rtp_stunaddr field '
                'when using engine_rtp_icesupport=true.'
            ),
            'example': False,
        },
    )
    engine_rtp_stunaddr = fields.String(
        validate=validate.Length(min=1, max=1024),
        load_default=None,
        metadata={
            'description': 'The address of the STUN server to use for WebRTC',
            'example': 'stun.example.com:3478',
        },
    )
    nestbox_host = fields.String(
        metadata={
            'description': (
                'Host of the Nestbox where the engine will register. '
                'Specifying this key will make nestbox and engine_internal_address '
                'keys mandatory. Wazo will be connected to the specified Nestbox instance.'
            ),
            'example': 'nestbox.example.com',
        },
    )
    nestbox_port = fields.Integer(
        validate=validate.Range(
            min=0, max=65535, error='Not a valid TCP/IP port number.'
        ),
        load_default=443,
        metadata={
            'description': 'Port of the Nestbox where the engine will register',
            'example': 443,
        },
    )
    nestbox_verify_certificate = fields.Boolean(
        load_default=True,
        metadata={
            'description': (
                'Should the certificate used for HTTPS be verified? '
                'The setup will abort if the certificate fails the verification.'
            ),
            'example': True,
        },
    )
    nestbox_service_id = fields.String(
        metadata={
            'description': 'Nestbox username used to register the engine',
            'example': 'wazo-engine-service',
        },
    )
    nestbox_service_key = fields.String(
        metadata={
            'description': 'Nestbox password used to register the engine',
            'example': 'secret-key',
        },
    )
    nestbox_instance_name = fields.String(
        metadata={
            'description': 'Name of the engine in Nestbox',
            'example': 'wazo-engine-01',
        },
    )
    nestbox_engine_host = fields.String(
        metadata={
            'description': 'Host used by Nestbox to contact the engine',
            'example': 'engine.example.com',
        },
    )
    nestbox_engine_port = fields.Integer(
        validate=validate.Range(
            min=0, max=65535, error='Not a valid TCP/IP port number.'
        ),
        load_default=443,
        metadata={
            'description': 'Port used by Nestbox to contact the engine',
            'example': 443,
        },
    )
    nestbox_instance_preferred_connection = fields.String(
        validate=validate.OneOf(['public', 'private']),
        load_default='public',
        metadata={
            'description': 'Preferred connection method to contact the engine',
            'example': 'public',
        },
    )

    @validates_schema
    def nestbox_all_or_nothing(self, data, **kwargs):
        if not data.get('nestbox_host'):
            return

        if 'nestbox_service_id' not in data:
            raise ValidationError(
                'Missing keys for Nestbox configuration: nestbox_service_id'
            )
        if 'nestbox_service_key' not in data:
            raise ValidationError(
                'Missing keys for Nestbox configuration: nestbox_service_key'
            )
        if 'nestbox_instance_name' not in data:
            raise ValidationError(
                'Missing keys for Nestbox configuration: nestbox_instance_name'
            )
        if 'nestbox_engine_host' not in data:
            raise ValidationError(
                'Missing keys for Nestbox configuration: nestbox_engine_host'
            )
        if 'engine_internal_address' not in data:
            raise ValidationError(
                'Missing keys for Nestbox configuration: engine_internal_address'
            )

    @validates_schema
    def check_rtp_fields(self, data, **kwargs):
        if not data.get('engine_rtp_icesupport'):
            return

        required_field = 'engine_rtp_stunaddr'
        if not data.get(required_field):
            raise ValidationError(
                f'Missing keys for rtp configuration: {required_field}',
                field_name=required_field,
            )


setup_schema = SetupSchema()
