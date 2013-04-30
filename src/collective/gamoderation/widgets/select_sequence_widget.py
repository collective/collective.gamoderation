
from zope.browserpage import ViewPageTemplateFile

from zope.formlib.widgets import SelectWidget


class SelectSequenceWidget(SelectWidget):
    """
    """

    size = None

    __call__ = ViewPageTemplateFile('select_sequence_widget.pt')

    def __init__(self, field, request):
        # SelectWidget expects the vocabulary as part of constructor
        super(SelectSequenceWidget, self).__init__(field,
                                                   field.vocabulary,
                                                   request)

    def render_widget(self):
        value = self._getFormValue()
        return self.renderValue(value)
