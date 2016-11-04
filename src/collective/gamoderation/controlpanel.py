

from zope.interface import Interface
from zope.interface import implements

from plone.autoform.form import AutoExtensibleForm
from z3c.form import button
from z3c.form.form import EditForm
from collective.gamoderation.interfaces import IAnalyticsModeration

from collective.gamoderation.widgets import SelectSequenceFieldWidget
from collective.gamoderation.widgets import BlockResultsFieldWidget

from collective.gamoderation import _

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from Products.statusmessages.interfaces import IStatusMessage

from zope.component.hooks import getSite

from zope.i18nmessageid import MessageFactory

_plone = MessageFactory('plone')


class IAnalyticsModerationControlPanelForm(Interface):
    """
    Google Analytics Moderation Control Panel Form
    """


class AnalyticsModerationControlPanelForm(AutoExtensibleForm, EditForm):
    """
    Google Analytics Moderation Control Panel Form
    """

    implements(IAnalyticsModerationControlPanelForm)

    label = _(u"Google Analytics (Moderation)")

    schema = IAnalyticsModeration

    def authorized(self):
        """
        Returns True if we have an auth token, or false otherwise.
        """

        return self.context.portal_analytics.is_auth()

    def updateFields(self):
        super(AnalyticsModerationControlPanelForm, self).updateFields()
        self.fields['moderated_channels'].widgetFactory = \
            SelectSequenceFieldWidget
        self.fields['block_results'].widgetFactory = BlockResultsFieldWidget

    def __call__(self):
        if not self.authorized():
            analytics_tool = (self.context.portal_analytics.absolute_url() +
                              "/@@analytics-controlpanel")
            return self.request.response.redirect(analytics_tool)
        else:
            reload_view = False
            if ('form.widgets.moderated_channels.select' in self.request.form or
                    'form.actions.save' in self.request.form):
                moderated_channel = self.request.form.get(
                    'form.widgets.moderated_channels')
                if moderated_channel:
                    self.request.set('moderated_channel', moderated_channel)
                else:
                    reload_view = True

            if 'form.widgets.moderated_channels.remove' in self.request.form:
                moderated_channel = self.request.form.get(
                    'form.widgets.moderated_channels')
                adapter = IAnalyticsModeration(self.context)
                adapter.remove_channel(moderated_channel)
                reload_view = True

            if 'form.widgets.moderated_channels.add' in self.request.form:
                moderated_channel = self.request.form.get(
                    'form.widgets.moderated_channels.new_value')
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

    def updateActions(self):
        super(AnalyticsModerationControlPanelForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _plone(u'Changes saved.'),
            'info')
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_plone(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _plone(u'Changes canceled.'),
            'info')
        self.request.response.redirect(u'{0}/{1}'.format(
            getSite().absolute_url(),
            '@@overview-controlpanel'
        ))


class AnalyticsModerationControlPanel(ControlPanelFormWrapper):

    form = AnalyticsModerationControlPanelForm
