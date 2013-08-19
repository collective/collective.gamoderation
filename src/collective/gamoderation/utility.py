
from zope import schema

from zope.component import getUtility

from zope.interface import implements

from plone.i18n.normalizer import idnormalizer

from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.registry import field

from collective.gamoderation.interfaces import IAnalyticsModerationUtility
from collective.gamoderation.interfaces import IAnalyticsModeration


class AnalyticsModerationUtility(object):
    implements(IAnalyticsModerationUtility)

    def __init__(self):
        self.fields = IAnalyticsModeration
        self.prefix = "%s.%s" % (self.fields.__module__, self.fields.__name__)
        self.cache_results = {}

    def add_channel(self, channel):
        registry = getUtility(IRegistry)
        # Adds a channel to the list of channels
        moderated_channel = idnormalizer.normalize(channel)
        # XXX: We cannot use a dash as part of a records key. Change it to
        #      an underscore here
        moderated_channel = moderated_channel.replace('-', '_')
        key = "%s.moderated_channels" % self.prefix
        channels = registry.get(key, None)

        if channels is None:
            # Create the record if it doesn't exist yet
            record = Record(field.List(), [])
            registry.records[key] = record
            channels = registry.get(key)

        channel_ids = [i[0] for i in channels]
        if moderated_channel in channel_ids:
            index = 1
            while "%s_%s" % (moderated_channel, index) in channel_ids:
                index += 1
            moderated_channel = "%s_%s" % (moderated_channel, index)

        channels.append((moderated_channel, channel))
        registry[key] = channels

    def remove_channel(self, channel):
        registry = getUtility(IRegistry)
        key = "%s.moderated_channels" % self.prefix
        channels = registry.get(key, [])
        for pair in channels:
            if pair[0] == channel:
                # Found a channel
                channels.remove(pair)
                registry[key] = channels
                # Cleanup other records
                self._cleanup_channel_records(channel)

    def get_channels(self):
        registry = getUtility(IRegistry)
        key = "%s.moderated_channels" % self.prefix
        channels = registry.get(key, [])
        return channels

    def add_property_for_channel(self, channel, property_name, value):
        registry = getUtility(IRegistry)
        key = "%s.%s.%s" % (self.prefix, channel, property_name)

        interface_field = self.fields[property_name]

        if isinstance(interface_field, schema.Choice):
            vocab = interface_field.vocabularyName
            record = Record(field.Choice(vocabulary=vocab), value)

        if isinstance(interface_field, schema.TextLine):
            record = Record(field.TextLine(title=interface_field.title), value)

        if isinstance(interface_field, schema.List):
            record = Record(field.List(), value)

        registry.records[key] = record

    def get_property_for_channel(self, channel, property_name):
        registry = getUtility(IRegistry)
        default = self.fields[property_name].default
        key = "%s.%s.%s" % (self.prefix, channel, property_name)
        value = registry.get(key, default)
        return value

    def _cleanup_channel_records(self, channel):
        registry = getUtility(IRegistry)
        # Handle the cleanup needed when removing a channel from the
        # registry
        fields = [i for i in self.fields if i != 'moderated_channels']
        for field_name in fields:
            key = key = "%s.%s.%s" % (self.prefix, channel, field_name)
            if key in registry:
                del registry.records[key]
