
from collective.gamoderation.interfaces import IAnalyticsModeration
from collective.gamoderation.interfaces import IBlockResultsWidget
from z3c.form import util as z3c_form_util
from z3c.form.browser import widget
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.term import Terms
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IList
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


class ResultsTerms(Terms):

    def __init__(self, context, request, form, field, widget, results):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        ids = set([z3c_form_util.toUnicode(elem['ga:pagePath'])
                   for elem in results])
        terms = [SimpleTerm(value=id, token=id, title=u"") for id in ids]
        self.terms = SimpleVocabulary(terms)


@implementer_only(IBlockResultsWidget)
class BlockResultsWidget(CheckBoxWidget):
    """
    """

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        self.analytics_moderation = IAnalyticsModeration(self.context)
        self.analytics_tool = self.context.portal_analytics
        self.results = self.analytics_moderation.query_google_analytics()

        self.terms = ResultsTerms(self.context, self.request, self.form,
                                  self.field, self, [])

        if self.has_valid_dimension():
            self.terms = ResultsTerms(self.context, self.request, self.form,
                                      self.field, self, self.results)
            self.filtered_results = self.analytics_moderation.filter_results(
                self.results)
        super(CheckBoxWidget, self).update()
        widget.addFieldClass(self)

    def items(self):
        items = []
        current_blocked = self.analytics_moderation.block_results
        headers = self.headers()
        for count, result in enumerate(self.results):
            value = result['ga:pagePath']
            checked = current_blocked and value in current_blocked
            auto_blocked = result not in self.filtered_results
            id = '%s-%i' % (self.id, count)
            label = z3c_form_util.toUnicode(value)
            item = {'id': id, 'name': self.name + ':list', 'value': value,
                    'label': label, 'checked': checked,
                    'auto_blocked': auto_blocked}
            for header in headers:
                item[header] = result[header]
            items.append(item)

        return items

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


@adapter(IList, Interface, IFormLayer)
@implementer(IFieldWidget)
def BlockResultsFieldWidget(field, source, request=None):
    """IFieldWidget factory for BlockResultsWidget."""
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, BlockResultsWidget(real_request))
