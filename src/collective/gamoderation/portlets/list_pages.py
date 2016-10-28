
from zope.component import getMultiAdapter

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.gamoderation import _


class IListPagesPortlet(IPortletDataProvider):
    """A portlet that will show a list of pages as returned by the
    moderated google analytics report
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"The header to be displayed"),
        required=True)

    max_results = schema.Int(
        title=_(u"Maximum results"),
        description=_(u"The maximum results to show"),
        default=5,
        required=True)

    moderated_channel = schema.Choice(
        title=_(u'Moderated channel'),
        description=_(u"Make sure you choose a channel that includes "
                      "ga:pagePath."),
        vocabulary="collective.gamoderation.ModeratedChannels",
        required=True)


class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(IListPagesPortlet)

    header = u""
    max_results = 5
    moderated_channel = u""

    def __init__(self, header=u"", max_results=5, moderated_channel=u""):
        self.header = header
        self.max_results = max_results
        self.moderated_channel = moderated_channel

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("List Google Analytics moderated pages")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('list_pages.pt')

    def get_header(self):
        """ Returns the header for the portlet.
        """
        return self.data.header

    def get_results(self):
        max_results = self.data.max_results
        channel = self.data.moderated_channel

        view = getMultiAdapter(
            (self.context, self.request),
            name="filtered-results"
        )

        results = view.get_results(channel)[:max_results]
        return results


class AddForm(base.AddForm):
    """Portlet add form.
    """
    schema = IListPagesPortlet

    label = _(u'Add List Pages Portlet.')
    description = _(u'')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    schema = IListPagesPortlet

    label = _(u'Edit List Pages Portlet.')
    description = _(u'')
