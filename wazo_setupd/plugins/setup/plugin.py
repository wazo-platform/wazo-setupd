# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resources import SetupResource
from .service import SetupService


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = SetupService(dependencies['stopper'])
        api.add_resource(SetupResource, '/setup', resource_class_args=[service])
