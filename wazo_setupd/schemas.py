# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields
from xivo.mallow_helpers import Schema


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
        values=fields.String(),
        metadata={
            'description': (
                'Additional information about the error. '
                'The keys are specific to each error.'
            )
        },
    )
    timestamp = fields.DateTime(
        format='timestamp', metadata={'description': 'Time when the error occurred'}
    )
