# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_key,
    calling,
    has_properties,
)

from wazo_setupd_client.exceptions import SetupdError
from xivo_test_helpers.hamcrest.raises import raises

from .helpers.base import (
    BaseIntegrationTest,
    VALID_TOKEN,
    VALID_MASTER_TOKEN,
    VALID_SUB_TOKEN,
    MASTER_TENANT,
    SUB_TENANT,
)
from .helpers.wait_strategy import NoWaitStrategy


class TestConfig(BaseIntegrationTest):

    asset = 'base'
    wait_strategy = NoWaitStrategy()

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
