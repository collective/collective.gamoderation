
from zope.app.component.hooks import getSite

from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from collective.googleanalytics.interfaces.report import \
    IAnalyticsReportRenderer

from collective.gamoderation.interfaces import IAnalyticsModerationUtility


class AnalyticsModeration(object):
    """
    Store and get values for the moderation in the registry
    """

    def __init__(self, context):
        self.context = context
        self.utility = getUtility(IAnalyticsModerationUtility)
        self.analytics_tool = getToolByName(context, 'portal_analytics')

    def set_moderated_channels(self, value):
        # Ignore storing any value
        return

    def get_moderated_channels(self):
        return self._get_moderated_channel()

    moderated_channels = property(get_moderated_channels,
                                  set_moderated_channels)

    def set_reports(self, value):
        channel = self._get_moderated_channel()
        if channel:
            self.utility.add_property_for_channel(channel, 'reports', value)

    def get_reports(self):
        channel = self._get_moderated_channel()
        return self.utility.get_property_for_channel(channel, 'reports')

    reports = property(get_reports, set_reports)

    def set_custom_query(self, value):
        channel = self._get_moderated_channel()
        if channel:
            self.utility.add_property_for_channel(
                channel, 'custom_query', value)

    def get_custom_query(self):
        channel = self._get_moderated_channel()
        return self.utility.get_property_for_channel(channel, 'custom_query')

    custom_query = property(get_custom_query, set_custom_query)

    def set_results_filter(self, value):
        channel = self._get_moderated_channel()
        if channel:
            self.utility.add_property_for_channel(
                channel, 'results_filter', value)

    def get_results_filter(self):
        channel = self._get_moderated_channel()
        return self.utility.get_property_for_channel(channel, 'results_filter')

    results_filter = property(get_results_filter, set_results_filter)

    def set_block_results(self, value):
        channel = self._get_moderated_channel()
        if channel:
            self.utility.add_property_for_channel(
                channel, 'block_results', value)

    def get_block_results(self):
        channel = self._get_moderated_channel()
        return self.utility.get_property_for_channel(channel, 'block_results')

    block_results = property(get_block_results, set_block_results)

    def remove_channel(self, channel):
        self.utility.remove_channel(channel)

    def add_channel(self, moderated_channel):
        self.utility.add_channel(moderated_channel)

    def query_google_analytics(self, channel=None):
        results = []
        request = self.context.REQUEST
        if not channel:
            channel = self._get_moderated_channel()

        report_id = self.utility.get_property_for_channel(channel, 'reports')
        if report_id:
            # If there is a report for this channel, use it to get results
            profile = getattr(self.analytics_tool, 'reports_profile', None)
            report = self.analytics_tool.get(report_id)
            if profile and report:
                request.set('profile_ids', profile)
                renderer = getMultiAdapter(
                    (self.context, request, report),
                    interface=IAnalyticsReportRenderer
                )
                results = renderer.data()
        else:
            # If there's no report, check to see if there's a custom_query
            # script provided
            custom_query = self.utility.get_property_for_channel(
                channel, 'custom_query'
            )
            if custom_query:
                # If there is, use it
                site = getSite()
                script = getattr(site, custom_query, None)
                try:
                    results = script()
                except:
                    pass

        return results

    def filter_results(self, data=None):
        # Filter results
        if not data:
            # If there's no data, query GA for them
            data = self.query_google_analytics()
        results = data
        if self.results_filter:
            # If the script was provided, call it with the data
            script = getattr(self.context, self.results_filter, None)
            if script:
                results = script(data)
        return results

    def _get_moderated_channel(self):
        # Get the channel chosen, from the request. If there's no channel, then
        # return the first one.
        # None if there is no channel in the system
        request = self.context.REQUEST
        channel = request.get('moderated_channel', None)
        if not channel:
            channels = self.utility.get_channels()
            if channels:
                channel = channels[0][0]

        return channel
