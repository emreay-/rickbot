import re
from typing import Pattern
from abc import ABC, abstractmethod

from message_payload import InboundMessagePayload, get_message_text_from_inbound_payload


class Condition(ABC):
    @abstractmethod
    def __call__(self, payload: InboundMessagePayload) -> bool:
        raise NotImplementedError("")


class BroadcastCommand:
    def __init__(self, command_name: str):
        self._command_name = command_name
        self._build()

    def _build(self):
        self._command = f"<!{self._command_name}>"

    def to_string(self):
        return self._command


class RegexMatchCondition(Condition):
    def __init__(self, pattern: Pattern):
        self._pattern = pattern

    def __call__(self, payload: InboundMessagePayload) -> bool:
        return self._pattern.search(
            get_message_text_from_inbound_payload(payload))


class OnAnyBroadcastCommandCondition(RegexMatchCondition):
    def __init__(self):
        command_strings = [
            BroadcastCommand("here").to_string(),
            BroadcastCommand("channel").to_string(),
            BroadcastCommand("all").to_string()
        ]

        super().__init__(re.compile('|'.join(command_strings)))
