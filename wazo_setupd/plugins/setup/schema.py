# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import Schema
from xivo.mallow import (
    fields,
    validate,
)


class SetupSchema(Schema):
    class Meta:
        strict = True

    engine_entity_name = fields.String(required=True)
    engine_language = fields.String(required=True)
    engine_number_start = fields.String(required=True)
    engine_number_end = fields.String(required=True)
    engine_password = fields.String(required=True)
    engine_internal_address = fields.String(required=True)
    nestbox_host = fields.String(required=True)
    nestbox_port = fields.Integer(
        required=True,
        validate=validate.Range(
            min=0,
            max=65535,
            error='Not a valid TCP/IP port number.'
        )
    )
    nestbox_verify_certificate = fields.Boolean(missing=True)
    nestbox_service_id = fields.String(required=True)
    nestbox_service_key = fields.String(required=True)
    nestbox_instance_name = fields.String(required=True)
    nestbox_engine_host = fields.String(required=True)
    nestbox_engine_port = fields.Integer(
        required=True,
        validate=validate.Range(
            min=0,
            max=65535,
            error='Not a valid TCP/IP port number.'
        )
    )


setup_schema = SetupSchema()
