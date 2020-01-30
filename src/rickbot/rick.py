import re
import time
import random
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
    ("repair", "It's time for some hands-on engine repair. All right, Morty, hold on to something."),
    ("society", "It's society! They work for each other, Morty. They pay each other, they buy houses, they get married and make children that replace them when they get too old to make power."),
    ("extra steps", "Ooh-la-la, someone's gonna get laid in college"),
    ("pickle", "I turned myself into a pickle, Morty! Boom! Big reveal! I'm a pickle! What do you think about that? I turned myself into a pickle! W-what are you just staring at me for, bro? I turned myself into a pickle, Morty.")
]

responses_for_broadcast_messages = [
    "Who dis?",
    "So I wouldn't have to come here... Because I don't respect therapy. Because I'm a scientist. Because I invent, transform, create, and destroy for a living, and when I don't like something about the world, I change it. And I don't think going to a rented office in a strip mall to listen to some agent of averageness explain which words mean which feelings has ever helped anyone do anything. I think it's helped a lot of people get comfortable and stop panicking, which is a state of mind [belch] we value in the animals we eat, but not something I want for myself. I'm not a cow. I'm a pickle. When I feel like it. So... you asked.",
    "Huh. Well, here's the problem right here. We've got a bunch of Froopy Land procedural carbons all gummed up and mixed in with real human DNA.",
    "Hey, Bloom, it's Rick. What the hell's going on here?",
    "All right, all right, cool it! I see what's happening here. You're both young, you're both unsure about your place in the universe, and you both want to be Grandpa's favorite. I can fix this. Morty, sit here. Summer, you sit here. Now, listen—I know the two of you are very different from each other in a lot of ways, but you have to understand that as far as Grandpa's concerned, you're both pieces of sh*t! Yeah. I can prove it mathematically. Actually, l-l-let me grab my whiteboard. This has been a long time coming, anyways."
]


class RickBot(Bot):
    def __init__(self, post_message: Callable[[OutboundMessagePayload], None],
                 sleep_after_response: Seconds = Seconds(5.0)):
        super().__init__()
        self._post_message = post_message
        self._sleep_after_action = sleep_after_response

        self._condition_and_callback_tuples: List[Tuple[ConditionFunction, CallbackFunction]] = [
            (OnAnyBroadcastCommandCondition(),
             self._make_message_response_function(responses_for_broadcast_messages))
        ]
        self._condition_and_callback_tuples += [
            (RegexMatchCondition(re.compile(_pattern)),
             self._make_message_response_function([_msg]))
            for _pattern, _msg in pattern_and_message_tuples
        ]
        self._last_action_time = None

    def _make_message_response_function(self, messages: List[str]) -> CallbackFunction:
        def _on_satisfied_condition(payload: InboundMessagePayload):
            self._post_message(
                OutboundMessagePayloadBuilder(
                    channel=get_channel_from_inbound_payload(payload),
                    user_id=get_user_id_from_inbound_payload(payload)
                ).add_block(BlockType.Section, text=random.choice(messages)).build()
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
