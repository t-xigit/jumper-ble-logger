import struct

"""
{
    1: {
        "type":"RadioEvent",
        "data": [
            "is_on": "B", //also possible to write "Byte" and convert to B ? 
            "channel: "B"
        ]
    },
    5: {
    ...
    }

}
"""


class EventParserException(Exception):
    pass


class EventParser(object):
    LOGGER_EVENT_HEADER = "<LLLL"
    LOGGER_EVENT_HEADER_LENGTH = struct.calcsize(LOGGER_EVENT_HEADER)

    def __init__(self, config):
        self.events_dict = config

    def parse(self, data):
        if len(data) < self.LOGGER_EVENT_HEADER_LENGTH:
            raise EventParserException('Data header too short')

        header = data[:self.LOGGER_EVENT_HEADER_LENGTH]
        body = data[self.LOGGER_EVENT_HEADER_LENGTH:]
        version, event_type_id, timestamp, data_length = struct.unpack(self.LOGGER_EVENT_HEADER, header)

        event_config = self.events_dict.get(event_type_id, None)

        if not event_config:
            return dict(
                event=event_type_id
            )

        event_dict = dict(
            type=event_config['type'],
            timestamp=timestamp
        )

        if event_config['data']:
            event_dict.update(self.parse_body(body, event_config['data']))

        return event_dict

    def parse_body(self, body, event_config):
        struct_format = ''.join(event_config.values())

        if len(body) < struct.calcsize(struct_format):
            raise EventParserException('Data body is too short')

        values = struct.unpack(struct_format, body)

        return {value_key: value for value_key, value in zip(event_config.keys(), values)}

