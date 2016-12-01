
import json
import logging
import sys
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from collective.gamoderation.config import PROJECTNAME
from collective.gamoderation.interfaces import IAnalyticsModerationUtility
from collective.googleanalytics.error import BadAuthenticationError
from collective.googleanalytics.interfaces.report import \
    IAnalyticsReportRenderer
from datetime import datetime
from persistent.mapping import PersistentMapping
from plone.protect.auto import safeWrite
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite

# Cache in seconds
CACHE = 1800

logger = logging.getLogger(PROJECTNAME)


class FilteredResults(BrowserView):

    def __init__(self, *args, **kwargs):
        super(FilteredResults, self).__init__(*args, **kwargs)
        self.site = getSite()
        self.analytics_tool = getToolByName(self.site, 'portal_analytics')
        self.utility = getUtility(IAnalyticsModerationUtility)

        analytics_tool = aq_base(self.analytics_tool)
        self.cached_results = getattr(analytics_tool, '_cached_results', None)

        if not self.cached_results:
            self.cached_results = analytics_tool._cached_results = \
                PersistentMapping()
        safeWrite(self.cached_results)

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
        local_data = self.cached_results.get(channel, {})
        if local_data:
            # We already have results saved. Check how old they are
            now = datetime.now()
            saved = local_data.get('date', datetime(2000, 1, 1))
            if (now - saved).seconds > CACHE * 2:
                # If 2*CACHE time has passed, update
                try:
                    self.update_values(channel)
                except BadAuthenticationError:
                    # Authentication with Google has been lost, leave old data
                    # untouched, and log in the error_log
                    self.site.error_log.raising(sys.exc_info())
        else:
            # No data for this channel.
            try:
                self.update_values(channel)
            except BadAuthenticationError:
                # Authentication with Google has been lost, just don't fail
                # and log in the error_log
                self.site.error_log.raising(sys.exc_info())

        local_data = self.cached_results.get(channel, {})
        results = []
        if local_data:
            results = local_data.get('results', [])
        return results

    def update_values(self, channel=None):
        objects = []
        # If no channel was provided, update all of them
        if not channel:
            channels = [i[0] for i in self.utility.get_channels()]
        else:
            channels = [channel, ]
        for channel_name in channels:
            query_results = self.query_filtered_results(channel_name)
            results = []
            for i in query_results:
                obj = self._get_object_path(channel_name, i['ga:pagePath'])
                if obj and obj not in objects:
                    objects.append(obj)
                    results.append({'title': obj.title_or_id(),
                                    'url': obj.absolute_url()})

            if results:
                self.cached_results[channel_name] = {
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
            obj = site.unrestrictedTraverse(path)
            if getattr(aq_base(obj), 'absolute_url', None) is None:
                logger.debug('ignore non-contentish object: %s' % path)
                obj = None

            if obj:
                # At this point, we have an object, let's see if it is the
                # default layout or default page of its parent
                view = path.split('/')[-1]
                if getattr(obj.aq_parent, 'getDefaultLayout'):
                    default_view = obj.aq_parent.getDefaultLayout()
                    if default_view == view:
                        logger.debug('Object at %s is actually the default layout of its parent' % path)
                        return obj.aq_parent
                if getattr(obj.aq_parent, 'getDefaultPage'):
                    default_page = obj.aq_parent.getDefaultPage()
                    if default_page == view:
                        logger.debug('Object at %s is actually the default page of its parent' % path)
                        return obj.aq_parent
        except:
            # We cannot traverse to the path, it might be a template or a view
            # remove the ending part and try again
            logger.debug("We couldn't find an object for: %s maybe is it a view?" % path)
            new_path,view = ('/'.join(path.split('/')[:-1]), path.split('/')[-1])
            try:
                obj = site.unrestrictedTraverse(new_path)
            except:
                logger.debug("No object found for %s. Giving up..." % new_path)
                return None

            # Found an object, see if it is contentish
            if getattr(aq_base(obj), 'absolute_url', None) is None:
                logger.debug('ignore non-contentish object: %s' % new_path)
                return None

            # Ok, we have an object... let's check the last part
            try:
                getMultiAdapter((object, self.request), name=view)
                # Found a view, so just return this object
                logger.debug("%s is a z3 view for %s" % (view, new_path))
                return obj
            except ComponentLookupError:
                logger.debug("%s is not a z3 view for %s" % (view, new_path))
                pass

            try:
                getattr(obj, view)
                logger.debug("%s is a template or callable for %s" % (view, new_path))
                return obj
            except AttributeError:
                logger.debug("%s is not a template nor callable for %s" % (view, new_path))
                obj = None

        return obj

    def _get_object_path(self, channel_name, path):
        new_path = path
        includes_host = self.utility.path_includes_host(channel_name)
        if includes_host:
            logger.debug("Channel configured to strip host from path")
            found = False
            hosts = self.utility.site_hosts(channel_name).split('\n')
            for host in hosts:
                if path.startswith(host):
                    new_path = path[len(host):]
                    found = True
                    # No need to continue
                    break
            if found:
                logger.debug("Identified and removed '%s' host in path" % host)
            else:
                logger.debug("Did not identify any valid host in path")

        else:
            logger.debug("Channel configured to assume paths do not have host")

        return self._get_object_from_rel_path(new_path)
