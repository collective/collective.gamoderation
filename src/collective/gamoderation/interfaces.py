
from collective.gamoderation import _
from z3c.form.interfaces import ICheckBoxWidget
from z3c.form.interfaces import ISelectWidget
from zope import schema
from zope.interface import Interface


class IAnalyticsModeration(Interface):
    """
    """

    moderated_channels = schema.Choice(
        title=_(u'Moderated Channels'),
        description=_(u'Each one of these, allows to moderate the results of '
                      'specific report, before rendering it.'),
        vocabulary="collective.gamoderation.ModeratedChannels",
        required=True)

    reports = schema.Choice(
        title=_(u"Reports"),
        vocabulary='collective.googleanalytics.SiteWideReports',
        description=_(u"Choose the reports to display."),
        required=False)

    custom_query = schema.TextLine(
        title=_(u"Custom query"),
        default=u"",
        description=_(u"You can specify here a python script which exists at "
                      "site root level to do the query."),
        required=False)

    results_filter = schema.TextLine(
        title=_(u"Results filter"),
        default=u"",
        description=_(u"You can specify here a python script which exists at "
                      "site root level to automatically filter results."),
        required=False)

    path_includes_host = schema.Bool(
        title=_(u"ga:pagePath includes host"),
        default=False,
        description=_(u"Check this if the results coming from Google "
                      "Analytics are not relative paths, and instead "
                      "use the full URL."),
        required=False)

    site_hosts = schema.Text(
        title=_(u"Site hosts"),
        default=u"",
        description=_(u"List here every host configured for this site. "
                       "One per line."),
        required=False)

    block_results = schema.List(
        title=_(u"Block results"),
        default=[],
        value_type=schema.TextLine(title=(u"Page path")),
        description=_(u"Choose which results to block."),
        required=False)


class IAnalyticsModerationUtility(Interface):
    """
    """

    def add_channel(channel):
        """ Adds a channel to the moderated channels list
        """

    def removes_channel(channel):
        """ Removes a channel to the moderated channels list
        """

    def get_channels():
        """ Returns a list of available channels
        """

    def add_property_for_channel(channel, property_name, value):
        """ Given a channel and a property, it will create a registry
        record for it and save its value
        """

    def get_property_for_channel(channel, property_name):
        """ Given a channel and a property name, return its stored value
        """


class ISelectSequenceWidget(ISelectWidget):
    """"""


class IBlockResultsWidget(ICheckBoxWidget):
    """"""
