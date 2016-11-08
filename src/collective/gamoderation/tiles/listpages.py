# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import DefaultConfigureForm
from collective.cover.tiles.configuration_view import DefaultConfigureView
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements


class ListPagesConfigureForm(DefaultConfigureForm):
    """
    """

    def updateWidgets(self):
        super(ListPagesConfigureForm, self).updateWidgets()
        self.widgets['max_results'].mode = HIDDEN_MODE
        self.widgets['moderated_channel'].mode = HIDDEN_MODE


class ListPagesConfigureView(DefaultConfigureView):
    """
    """
    form = ListPagesConfigureForm


class IListPagesTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"The title to be displayed"),
        required=False)

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


class ListPagesTile(PersistentCoverTile):

    implements(IListPagesTile)

    index = ViewPageTemplateFile("listpages.pt")

    is_configurable = True
    is_droppable = False
    is_editable = True

    def get_results(self):
        """ Return the list of objects stored in the tile.
        """
        results = []
        max_results = self.data.get('max_results', None)
        moderated_channel = self.data.get('moderated_channel', None)

        if moderated_channel:
            view = getMultiAdapter(
                (self.context, self.request),
                name="filtered-results"
            )

            results = view.get_results(moderated_channel)[:max_results]

        return results

    def is_empty(self):
        return self.get_results() == []

    #def accepted_ct(self):
        #"""
        #"""
        #return None
