
try:
    import json
except ImportError:
    import simplejson as json
from datetime import datetime

from zope.app.component.hooks import getSite

from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView

from collective.googleanalytics.interfaces.report import \
    IAnalyticsReportRenderer

from collective.gamoderation.interfaces import IAnalyticsModerationUtility

# Cache in seconds
CACHE = 1800


class FilteredResults(BrowserView):

    def __init__(self, *args, **kwargs):
        super(FilteredResults, self).__init__(*args, **kwargs)
        self.site = getSite()
        self.analytics_tool = getToolByName(self.site, 'portal_analytics')
        self.utility = getUtility(IAnalyticsModerationUtility)

    def __call__(self):
        channel = self.request.get('channel', None)
        if channel:
            data = self.get_results(channel)
        else:
            data = []

        self.headers()

        return json.dumps(data, encoding='utf-8', ensure_ascii=False)

    def headers(self):
        self.request.response.setHeader('Content-Type',
                                        'application/json;charset=utf-8')
        # Half hour cache both in browser and in proxy
        self.request.response.setHeader('Cache-Control',
                                        'max-age=%s, s-maxage=%s,public' %
                                        (CACHE, CACHE))

    def get_results(self, channel):
        if channel in self.utility.cache_results:
            # We already have results saved. Check how old they are
            local_data = self.utility.cache_results[channel]
            now = datetime.now()
            saved = local_data.get('date', datetime(2000, 1, 1))
            if (now - saved).seconds > CACHE * 2:
                # If 2*CACHE time has passed, update
                self.update_values(channel)
        else:
            # No data for this channel.
            self.update_values(channel)
        local_data = self.utility.cache_results.get(channel, {})
        results = local_data.get('results', [])
        return results

    def update_values(self, channel=None):
        # If no channel was provided, update all of them
        if not channel:
            channels = [i[0] for i in self.utility.get_channels()]
        else:
            channels = [channel, ]
        for channel_name in channels:
            query_results = self.query_filtered_results(channel_name)
            results = []
            for i in query_results:
                obj = self._get_object_from_rel_path(i['ga:pagePath'])
                if obj:
                    results.append({'title': obj.title,
                                    'url': obj.absolute_url()})

            self.utility.cache_results[channel_name] = {
                'date': datetime.now(),
                'results': results
            }

    def query_google_analytics(self, channel):
        results = []
        report_id = self.utility.get_property_for_channel(channel, 'reports')
        if report_id:
            # If there is a report for this channel, use it to get results
            profile = getattr(self.analytics_tool, 'reports_profile', None)
            report = self.analytics_tool.get(report_id)
            if profile and report:
                self.request.set('profile_ids', profile)
                renderer = getMultiAdapter(
                    (self.context, self.request, report),
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
                script = getattr(self.site, custom_query, None)
                try:
                    results = script()
                except:
                    pass

        return results

    def query_filtered_results(self, channel):
        results = self.query_google_analytics(channel)
        # Now, see if we have a filter script
        results_filter = self.utility.get_property_for_channel(
            channel, 'results_filter'
        )
        if results_filter:
            # If the script was provided, call it with the data
            script = getattr(self.site, results_filter, None)
            if script:
                results = script(results)

        # Now, check for manually blocked entries
        block_results = self.utility.get_property_for_channel(
            channel, 'block_results'
        )
        if block_results:
            results = [i for i in results
                       if i['ga:pagePath'] not in block_results]

        return results

    def _get_object_from_rel_path(self, path):
        site = getSite()
        if path.startswith('/'):
            path = path[1:]
        try:
            obj = site.restrictedTraverse(path)
            if not hasattr(obj, 'title') or \
               not hasattr(obj, 'absolute_url'):
                return None
        except:
            obj = None
        return obj
