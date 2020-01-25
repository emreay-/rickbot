import re
from typing import Callable, List, Tuple

from bot import Bot, ConditionFunction, CallbackFunction
from triggers import OnAnyBroadcastCommandCondition, RegexMatchCondition
from message_payload import (
    InboundMessagePayload, OutboundMessagePayload,
    OutboundMessagePayloadBuilder, BlockType,
    get_channel_from_inbound_payload, get_user_id_from_inbound_payload,
)


pattern_and_message_tuples = [
    (re.compile("love"), "Listen, Morty, I hate to break it to you but what people call 'love' is just a chemical reaction that compels animals to breed. It hits hard, Morty, then it slowly fades, leaving you stranded in a failing marriage. I did it. Your parents are gonna do it. Break the cycle, Morty. Rise above. Focus on science"),
    (re.compile("exist"), "Nobody exists on purpose. Nobody belongs anywhere. We're all going to die. Come watch TV."),
    (re.compile("tough"), "Yeah, well, tough titties."),
    (re.compile("party"), "Get Schwifty!"),
    (re.compile("tunes"), "Get Schwifty!"),
    (re.compile("choones"), "Get Schwifty!"),
    (re.compile("hate"), "Welcome to the club, pal."),
    (re.compile("purpose"), "Your purpose? To pass butter..."),
    (re.compile("happy"), "Wubba Lubba Dub Dub!"),
    (re.compile("great"), "Wubba Lubba Dub Dub!"),
    (re.compile("exciting"), "Wubba Lubba Dub Dub!"),
]


class RickBot(Bot):
    def __init__(self, post_message: Callable[[OutboundMessagePayload], None]):
        super().__init__()
        self._post_message = post_message
        self._condition_and_callback_tuples: List[Tuple[ConditionFunction, CallbackFunction]] = [
            (OnAnyBroadcastCommandCondition(),
             self._make_message_response_function("Who dis?"))
        ]
        self._condition_and_callback_tuples += [
            (RegexMatchCondition(_cnd), self._make_message_response_function(_msg)) for _cnd, _msg in pattern_and_message_tuples
        ]

    def _make_message_response_function(self, message: str) -> CallbackFunction:
        def _on_satisfied_condition(payload: InboundMessagePayload):
            self._post_message(
                OutboundMessagePayloadBuilder(
                    channel=get_channel_from_inbound_payload(payload),
                    user_id=get_user_id_from_inbound_payload(payload)
                ).add_block(BlockType.Section, text=message).build()
            )
        return _on_satisfied_condition

    def respond_to_message(self, payload: InboundMessagePayload):
        self.dispatch_many_conditions(
            payload,
            self._condition_and_callback_tuples
        )
