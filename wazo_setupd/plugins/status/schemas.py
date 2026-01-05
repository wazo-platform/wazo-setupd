# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import Schema, fields, validate


class ComponentWithStatusSchema(Schema):
    """Status of an individual component."""

    status = fields.String(
        validate=validate.OneOf(['ok', 'fail']),
        metadata={'description': 'Component health status'},
    )


class StatusSummarySchema(Schema):
    """Service status response with component health checks."""

    rest_api = fields.Nested(
        ComponentWithStatusSchema,
        metadata={'description': 'REST API component status'},
    )
    master_tenant = fields.Nested(
        ComponentWithStatusSchema,
        metadata={'description': 'Master tenant initialization status'},
    )
