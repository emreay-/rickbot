import re
import time
from functools import wraps
from typing import Callable, List, Tuple, NewType

from bot import Bot, ConditionFunction, CallbackFunction
from triggers import OnAnyBroadcastCommandCondition, RegexMatchCondition
from message_payload import (
    InboundMessagePayload, OutboundMessagePayload,
    OutboundMessagePayloadBuilder, BlockType,
    get_channel_from_inbound_payload, get_user_id_from_inbound_payload,
)

Seconds = NewType("Seconds", float)

pattern_and_message_tuples = [
    ("love", "Listen, Morty, I hate to break it to you but what people call 'love' is just a chemical reaction that compels animals to breed. It hits hard, Morty, then it slowly fades, leaving you stranded in a failing marriage. I did it. Your parents are gonna do it. Break the cycle, Morty. Rise above. Focus on science"),
    ("exist", "Nobody exists on purpose. Nobody belongs anywhere. We're all going to die. Come watch TV."),
    ("tough", "Yeah, well, tough titties."),
    ("party", "Get Schwifty!"),
    ("tunes", "Get Schwifty!"),
    ("choones", "Get Schwifty!"),
    ("hate", "Welcome to the club, pal."),
    ("purpose", "Your purpose? To pass butter..."),
    ("happy", "Wubba Lubba Dub Dub!"),
    ("great", "Wubba Lubba Dub Dub!"),
    ("exciting", "Wubba Lubba Dub Dub!"),
]


class RickBot(Bot):
    def __init__(self, post_message: Callable[[OutboundMessagePayload], None], 
                 sleep_after_response: Seconds = Seconds(5.0)):
        super().__init__()
        self._post_message = post_message
        self._sleep_after_action = sleep_after_response

        self._condition_and_callback_tuples: List[Tuple[ConditionFunction, CallbackFunction]] = [
            (OnAnyBroadcastCommandCondition(),
             self._make_message_response_function("Who dis?"))
        ]
        self._condition_and_callback_tuples += [
            (RegexMatchCondition(re.compile(_pattern)), self._make_message_response_function(_msg)) 
            for _pattern, _msg in pattern_and_message_tuples
        ]
        self._last_action_time = None

    def _make_message_response_function(self, message: str) -> CallbackFunction:
        def _on_satisfied_condition(payload: InboundMessagePayload):
            self._post_message(
                OutboundMessagePayloadBuilder(
                    channel=get_channel_from_inbound_payload(payload),
                    user_id=get_user_id_from_inbound_payload(payload)
                ).add_block(BlockType.Section, text=message).build()
            )
        return _on_satisfied_condition

    def _enforce_waiting(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._is_waiting_period():
                r = func(self, *args, **kwargs)
                self._update_action_time()
                return
        return wrapper

    def _is_waiting_period(self):
        return self._last_action_time is not None and \
               time.time() - self._last_action_time < self._sleep_after_action
    
    def _update_action_time(self):
        self._last_action_time = time.time()

    @_enforce_waiting
    def respond_to_message(self, payload: InboundMessagePayload):
        self.dispatch_many_conditions(
            payload,
            self._condition_and_callback_tuples
        )
