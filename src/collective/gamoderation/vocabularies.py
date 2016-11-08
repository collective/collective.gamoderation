
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def getModeratedChannels(context):
    """
    Returns list of Moderated channels.
    """

    registry = getUtility(IRegistry)
    prefix = 'collective.gamoderation.interfaces.IAnalyticsModeration.'
    channels = registry.get(prefix+"moderated_channels", [])
    terms = [SimpleTerm(value=channel[0], token=channel[0], title=channel[1])
             for channel in channels]

    return SimpleVocabulary(terms)
