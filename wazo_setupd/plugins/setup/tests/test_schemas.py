# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from hamcrest import assert_that, calling, has_entries, raises

from ..schemas import SetupSchema, ValidationError

STUNADDR_TOO_LONG = 'z' * 2048


class TestSetupSchema(TestCase):
    def test_rtp_fields(self):
        body = self._make_body()
        result = SetupSchema().load(body)
        assert_that(
            result,
            has_entries(
                engine_rtp_icesupport=False,
                engine_rtp_stunaddr=None,
            ),
        )

        body = self._make_body(
            engine_rtp_icesupport=True,
            engine_rtp_stunaddr='mystunserver:1234',
        )
        result = SetupSchema().load(body)
        assert_that(
            result,
            has_entries(
                engine_rtp_icesupport=True,
                engine_rtp_stunaddr='mystunserver:1234',
            ),
        )

        body = self._make_body(engine_rtp_icesupport=True)
        assert_that(
            calling(SetupSchema().load).with_args(body),
            raises(ValidationError),
        )

        body = self._make_body(
            engine_rtp_icesupport=True, engine_rtp_stunaddr=STUNADDR_TOO_LONG
        )
        assert_that(
            calling(SetupSchema().load).with_args(body),
            raises(ValidationError),
        )

    def _make_body(
        self,
        engine_language='en_US',
        engine_password='foobar',
        engine_license=True,
        **not_required
    ):
        return {
            'engine_language': engine_language,
            'engine_password': engine_password,
            'engine_license': engine_license,
            **not_required,
        }
