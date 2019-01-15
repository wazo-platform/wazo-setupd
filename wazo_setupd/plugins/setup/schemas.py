# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import Schema
from xivo.mallow import (
    fields,
    validate,
)


class SetupSchema(Schema):
    class Meta:
        strict = True

    engine_entity_name = fields.String(required=True)
    engine_language = fields.String(required=True, validate=validate.OneOf(['en_US', 'fr_FR']))
    engine_number_start = fields.String(required=True)
    engine_number_end = fields.String(required=True)
    engine_password = fields.String(required=True)
    engine_internal_address = fields.String(required=True)
    engine_license = fields.Boolean(required=True, validate=validate.Equal(True))
    nestbox_host = fields.String(required=True)
    nestbox_port = fields.Integer(
        validate=validate.Range(
            min=0,
            max=65535,
            error='Not a valid TCP/IP port number.'
        ),
        missing=443,
    )
    nestbox_verify_certificate = fields.Boolean(missing=True)
    nestbox_service_id = fields.String(required=True)
    nestbox_service_key = fields.String(required=True)
    nestbox_instance_name = fields.String(required=True)
    nestbox_engine_host = fields.String(required=True)
    nestbox_engine_port = fields.Integer(
        validate=validate.Range(
            min=0,
            max=65535,
            error='Not a valid TCP/IP port number.'
        ),
        missing=443,
    )


setup_schema = SetupSchema()
