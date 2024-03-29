# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
from hamcrest import assert_that, has_entries, has_entry
from wazo_test_helpers import until


class WaitStrategy:
    def wait(self, setupd):
        raise NotImplementedError()


class NoWaitStrategy(WaitStrategy):
    def wait(self, setupd):
        pass


class SetupdEverythingOkWaitStrategy(WaitStrategy):
    def wait(self, setupd):
        def setupd_is_ready():
            try:
                status = setupd.status.get()
            except requests.RequestException:
                status = {}
            assert_that(
                status,
                has_entries(
                    {
                        'rest_api': has_entry('status', 'ok'),
                        'master_tenant': has_entry('status', 'ok'),
                    }
                ),
            )

        until.assert_(setupd_is_ready, tries=60)
