# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
)
from xivo_test_helpers import until

from .helpers.base import (
    BaseIntegrationTest,
    VALID_TOKEN,
)
from .helpers.wait_strategy import NoWaitStrategy


class TestStatusAllOK(BaseIntegrationTest):

    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def test_when_status_then_status_ok(self):
        setupd = self.make_setupd(VALID_TOKEN)

        def status_ok():
            result = setupd.status.get()
            assert_that(result['rest-api'], has_entries({'status': 'ok'}))

        until.assert_(status_ok, timeout=5)
