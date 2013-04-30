
from zope.browserpage import ViewPageTemplateFile

from zope.formlib.widgets import MultiCheckBoxWidget

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


class BlockResultsWidget(MultiCheckBoxWidget):
    """
    """

    size = None

    __call__ = ViewPageTemplateFile('block_results_widget.pt')

    def _process_results(self, data):
        terms = []
        ids = set([unicode(elem['ga:pagePath']) for elem in data])
        terms = [SimpleTerm(value=id, token=id, title=u"") for id in ids]
        return SimpleVocabulary(terms)

    def __init__(self, field, request):
        self.analytics_moderation = field.context
        self.analytics_tool = field.context.context.portal_analytics
        self.results = self.analytics_moderation.query_google_analytics()

        # BlockResultsWidget expects the vocabulary as part of constructor
        super(BlockResultsWidget, self).__init__(
            field,
            [],
            request)
        if self.has_valid_dimension():
            self.vocabulary = self._process_results(self.results)
            self.filtered_results = self.analytics_moderation.filter_results(
                self.results)

    def has_valid_dimension(self):
        result = False
        if self.results:
            result = 'ga:pagePath' in self.results[0].keys()
        return result

    def headers(self):
        headers = []
        if self.results:
            headers = self.results[0].keys()
        return headers

    def render_checkbox(self, value, index):
        id = value['ga:pagePath']
        current_blocked = self.analytics_moderation.block_results
        if current_blocked and id in current_blocked:
            render = self.renderSelectedItem
        else:
            render = self.renderItem

        rendered_item = render(index,
                               "",
                               id,
                               self.name,
                               self.cssClass)

        return rendered_item
