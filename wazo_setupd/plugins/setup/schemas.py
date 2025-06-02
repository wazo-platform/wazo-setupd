# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import validates_schema
from marshmallow.exceptions import ValidationError
from xivo.mallow import fields, validate
from xivo.mallow_helpers import Schema


class SetupSchema(Schema):
    engine_language = fields.String(
        required=True, validate=validate.OneOf(['en_US', 'fr_FR'])
    )
    engine_password = fields.String(required=True)
    engine_license = fields.Boolean(required=True, validate=validate.Equal(True))
    engine_internal_address = fields.String()
    engine_instance_uuid = fields.UUID(load_default=None)
    engine_rtp_icesupport = fields.Boolean(required=False, load_default=False)
    engine_rtp_stunaddr = fields.String(
        validate=validate.Length(min=1, max=1024), load_default=None
    )
    nestbox_host = fields.String()
    nestbox_port = fields.Integer(
        validate=validate.Range(
            min=0, max=65535, error='Not a valid TCP/IP port number.'
        ),
        load_default=443,
    )
    nestbox_verify_certificate = fields.Boolean(load_default=True)
    nestbox_service_id = fields.String()
    nestbox_service_key = fields.String()
    nestbox_instance_name = fields.String()
    nestbox_engine_host = fields.String()
    nestbox_engine_port = fields.Integer(
        validate=validate.Range(
            min=0, max=65535, error='Not a valid TCP/IP port number.'
        ),
        load_default=443,
    )
    nestbox_instance_preferred_connection = fields.String(
        validate=validate.OneOf(['public', 'private']),
        load_default='public',
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
