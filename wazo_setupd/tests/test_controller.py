from mock import Mock
from unittest import TestCase

from ..controller import _sigterm_handler


class Testclassname(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sigterm_handler(self):
        _sigterm_handler(Mock(), Mock(), Mock())
