# -*- coding: utf-8 -*-

import doctest
import unittest2 as unittest

from plone.testing import layered

from collective.gamoderation.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('tests/functional.txt',
                                     package='collective.gamoderation'),
                layer=FUNCTIONAL_TESTING)
    ])
    return suite
