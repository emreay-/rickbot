import time
from typing import NewType
from enum import Enum, unique

MessagePayload = NewType("MessagePayload", dict)
InboundMessagePayload = NewType("InboundMessagePayload", MessagePayload)
OutboundMessagePayload = NewType("OutboundMessagePayload", MessagePayload)


@unique
class BlockType(Enum):
    Actions = "actions"
    Context = "context"
    Divider = "divider"
    File = "file"
    Image = "image"
    Input = "input"
    Section = "section"


class OutboundMessagePayloadBuilder:
    def __init__(self, channel: str, user_id: str, timestamp: float = time.time()):
        self._channel = channel
        self._user_id = user_id
        self._timestamp = timestamp
        self._blocks = []

    def add_block(self, block_type: BlockType, **kwargs) -> "OutboundMessagePayloadBuilder":
        block = {"type": block_type.value}

        if block_type is BlockType.Section:
            block.update(
                {
                    "text": {
                        "type": "mrkdwn",
                        "text": (kwargs.get("text")),
                    }
                }
            )
        else:
            raise NotImplementedError(f"Block type not yet supported {block_type.value}")

        self._blocks.append(block)
        return self

    def build(self) -> OutboundMessagePayload:
        return {
            "ts": self._timestamp,
            "channel": self._channel,
            "username": self._user_id,
            "blocks": self._blocks
        }


class CannotRetrieveDataFromPayloadError(Exception):
    def __init__(self, message: str = ''):
        super().__init__(message)


def get_message_text_from_inbound_payload(payload: InboundMessagePayload) -> str:
    try:
        return payload.get("event").get("text")
    except KeyError as e:
        raise CannotRetrieveDataFromPayloadError() from e


def get_channel_from_inbound_payload(payload: InboundMessagePayload) -> str:
    try:
        return payload.get("event").get("channel")
    except KeyError as e:
        raise CannotRetrieveDataFromPayloadError() from e


def get_user_id_from_inbound_payload(payload: InboundMessagePayload) -> str:
    try:
        return payload.get("event").get("user")
    except KeyError as e:
        raise CannotRetrieveDataFromPayloadError() from e
