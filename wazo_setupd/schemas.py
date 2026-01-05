# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import Schema, fields, validate


class ErrorSchema(Schema):
    """API error response schema."""

    message = fields.String(
        metadata={'description': 'Human readable explanation of the error'}
    )
    error_id = fields.String(
        metadata={
            'description': (
                'Identifier of the type of error. '
                'It is more precise than the HTTP status code.'
            )
        }
    )
    details = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        metadata={
            'description': (
                'Additional information about the error. '
                'The keys are specific to each error.'
            )
        },
    )
    timestamp = fields.Float(metadata={'description': 'Time when the error occurred'})


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
