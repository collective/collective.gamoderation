
from collective.gamoderation.interfaces import ISelectSequenceWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice


@implementer_only(ISelectSequenceWidget)
class SelectSequenceWidget(SelectWidget):
    """
    """


@adapter(IChoice, Interface, IFormLayer)
@implementer(IFieldWidget)
def SelectSequenceFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectSequenceWidget."""
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, SelectSequenceWidget(real_request))
