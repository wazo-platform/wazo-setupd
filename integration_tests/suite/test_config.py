# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, has_key, has_properties
from wazo_setupd_client.exceptions import SetupdError
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import VALID_SUB_TOKEN, VALID_TOKEN, BaseIntegrationTest
from .helpers.wait_strategy import SetupdEverythingOkWaitStrategy


class TestConfig(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = SetupdEverythingOkWaitStrategy()

    def test_config(self):
        setupd = self.make_setupd(VALID_TOKEN)

        result = setupd.config.get()

        assert_that(result, has_key('rest_api'))

    def test_restrict_only_master_tenant(self):
        setupd = self.make_setupd(VALID_SUB_TOKEN)

        assert_that(
            calling(setupd.config.get),
            raises(SetupdError).matching(has_properties(status_code=401)),
        )
