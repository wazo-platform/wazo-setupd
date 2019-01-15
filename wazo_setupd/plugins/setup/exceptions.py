# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.rest_api_helpers import APIException


class SetupError(APIException):
    def __init__(self, message, error_id, details=None):
        super().__init__(
            status_code=500,
            message=message,
            error_id=error_id,
            details=details,
            resource='setup',
        )
