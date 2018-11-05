# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import StatusResource


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(StatusResource, '/status', resource_class_args=[])
