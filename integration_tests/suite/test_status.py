# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries
from wazo_test_helpers import until

from .helpers.base import VALID_TOKEN, BaseIntegrationTest
from .helpers.wait_strategy import SetupdEverythingOkWaitStrategy


class TestStatusAllOK(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = SetupdEverythingOkWaitStrategy()

    def test_when_status_then_status_ok(self):
        setupd = self.make_setupd(VALID_TOKEN)

        def status_ok():
            result = setupd.status.get()
            assert_that(
                result,
                has_entries(
                    {
                        'rest_api': has_entries({'status': 'ok'}),
                        'master_tenant': has_entries({'status': 'ok'}),
                    },
                ),
            )

        until.assert_(status_ok, timeout=5)
