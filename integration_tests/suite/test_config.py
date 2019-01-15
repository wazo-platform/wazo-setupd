# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_key,
)

from .helpers.base import (
    BaseIntegrationTest,
    VALID_TOKEN,
)
from .helpers.wait_strategy import NoWaitStrategy


class TestConfig(BaseIntegrationTest):

    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def test_config(self):
        setupd = self.make_setupd(VALID_TOKEN)

        result = setupd.config.get()

        assert_that(result, has_key('rest_api'))
