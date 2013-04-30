# -*- coding: utf-8 -*-

from zope.component import getGlobalSiteManager

from zope.interface import implements
from zope.interface import Interface

from zope.publisher.interfaces import IRequest

from zope.schema.interfaces import IVocabularyFactory

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from collective.googleanalytics.interfaces.report import \
    IAnalyticsReportRenderer
from collective.googleanalytics.interfaces.report import IAnalyticsReport


class AnalyticsReportRenderer(object):
    """
    Override the report renderer to return whatever we want
    """

    implements(IAnalyticsReportRenderer)

    def __init__(self, context, request, report):
        self.context = context
        self.request = request
        self.report = report

    def data(self):
        # Just return whatever we want
        return [{'ga:pagePath': '/folder/page'}]


def getProfiles(context):
    elem = 'test-profile'
    return SimpleVocabulary([SimpleTerm(elem, elem, elem)])


def overrideAdaptersAndUtilities(context):
    # Register our own mutliadapter and vocabulary
    gsm = getGlobalSiteManager()

    gsm.registerUtility(getProfiles,
                        IVocabularyFactory,
                        name="collective.googleanalytics.Profiles")
    gsm.registerAdapter(AnalyticsReportRenderer,
                        (Interface, IRequest, IAnalyticsReport),
                        IAnalyticsReportRenderer)
    analytics_tool = context.portal_analytics
    analytics_tool.reports_profile = 'test-profile'


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.googleanalytics
        self.loadZCML(package=collective.googleanalytics)
        import collective.gamoderation
        self.loadZCML(package=collective.gamoderation)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.gamoderation:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.gamoderation:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='collective.gamoderation:Functional',
)
