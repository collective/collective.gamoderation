# -*- coding: utf-8 -*-

import doctest
import unittest2 as unittest
from collective.gamoderation.testing import FUNCTIONAL_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('tests/functional.txt',
                                     package='collective.gamoderation'),
                layer=FUNCTIONAL_TESTING)
    ])
    return suite
