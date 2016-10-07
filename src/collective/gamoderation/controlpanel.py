
from zope.formlib import form

from zope.interface import Interface
from zope.interface import implements


from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.googleanalytics.browser.controlpanel_form import \
    ControlPanelForm
from collective.gamoderation.interfaces import IAnalyticsModeration

from collective.gamoderation.widgets import SelectSequenceWidget
from collective.gamoderation.widgets import BlockResultsWidget

from collective.gamoderation import _


class IAnalyticsModerationControlPanelForm(Interface):
    """
    Google Analytics Moderation Control Panel Form
    """


class AnalyticsModerationControlPanelForm(ControlPanelForm):
    """
    Google Analytics Moderation Control Panel Form
    """

    implements(IAnalyticsModerationControlPanelForm)
    template = ViewPageTemplateFile('controlpanel.pt')

    label = _(u"Google Analytics (Moderation)")
    form_name = _("Google Analytics Moderation Settings")

    form_fields = form.FormFields(IAnalyticsModeration)

    form_fields['moderated_channels'].custom_widget = SelectSequenceWidget
    form_fields['block_results'].custom_widget = BlockResultsWidget

    def authorized(self):
        """
        Returns True if we have an auth token, or false otherwise.
        """

        return self.context.portal_analytics.is_auth()

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {IAnalyticsModeration:
                         IAnalyticsModeration(self.context)}

        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=True
        )

    def __call__(self):
        if not self.authorized():
            analytics_tool = (self.context.portal_analytics.absolute_url() +
                              "/@@analytics-controlpanel")
            return self.request.response.redirect(analytics_tool)
        else:
            reload_view = False
            if ('form.moderated_channels.select' in self.request.form or
                    'form.actions.save' in self.request.form):
                moderated_channel = self.request.form.get(
                    'form.moderated_channels')
                if moderated_channel:
                    self.request.set('moderated_channel', moderated_channel)
                else:
                    reload_view = True

            if 'form.moderated_channels.remove' in self.request.form:
                moderated_channel = self.request.form.get(
                    'form.moderated_channels')
                adapter = IAnalyticsModeration(self.context)
                adapter.remove_channel(moderated_channel)
                reload_view = True

            if 'form.moderated_channels.add' in self.request.form:
                moderated_channel = self.request.form.get(
                    'form.moderated_channels.new_value')
                adapter = IAnalyticsModeration(self.context)
                adapter.add_channel(moderated_channel)
                reload_view = True

            if reload_view:
                view = (self.context.absolute_url() +
                        "/@@analytics-moderation-controlpanel")
                return self.request.response.redirect(view)
            else:
                return super(
                    AnalyticsModerationControlPanelForm, self).__call__()
