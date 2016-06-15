
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

    def add_channel(self, channel):
        registry = getUtility(IRegistry)
        # Adds a channel to the list of channels
        moderated_channel = idnormalizer.normalize(channel)
        # XXX: We cannot use a dash as part of a records key. Change it to
        #      an underscore here
        moderated_channel = moderated_channel.replace('-', '_')
        # XXX: a registry key cannot start with a number
        #     https://github.com/plone/plone.registry/blob/645163c7b956b3e5541f8b907f786353b3e06eaa/plone/registry/registry.py#L144
        if not moderated_channel[0].isalpha():
            moderated_channel = "id_%s" % moderated_channel
        key = "%s.moderated_channels" % self.prefix
        channels = registry.get(key, None)

        if channels is None:
            # Create the record if it doesn't exist yet
            _field = field.List()
            _field.value_type = field.Tuple()
            _field.value_type.value_type = field.TextLine()
            record = Record(_field, [])
            registry.records[key] = record
            channels = registry.get(key)

        channel_ids = [i[0] for i in channels]
        if moderated_channel in channel_ids:
            index = 1
            while "%s_%s" % (moderated_channel, index) in channel_ids:
                index += 1
            moderated_channel = u"%s_%s" % (moderated_channel, index)

        channels.append((unicode(moderated_channel), unicode(channel)))
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
            _field = field.List()
            if isinstance(interface_field.value_type, schema.TextLine):
                _field.value_type = field.TextLine()
            if isinstance(interface_field.value_type, schema.ASCIILine):
                _field.value_type = field.ASCIILine()
            record = Record(_field, value)

        if isinstance(interface_field, schema.Text):
            record = Record(field.Text(), value)

        if isinstance(interface_field, schema.Bool):
            record = Record(field.Bool(), value)

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

    def path_includes_host(self, channel_name):
        value = self.get_property_for_channel(channel_name, "path_includes_host")
        return value

    def site_hosts(self, channel_name):
        value = self.get_property_for_channel(channel_name, "site_hosts")
        return value
