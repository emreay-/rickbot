from typing import Callable, List, Tuple
from abc import ABC, abstractmethod

from message_payload import InboundMessagePayload, get_message_text_from_inbound_payload


ConditionFunction = Callable[[InboundMessagePayload], bool]
CallbackFunction = Callable[[InboundMessagePayload], None]


def _count_up(func: Callable):
    def wrapper(self, *args, **kwargs):
        self._call_count += 1
        func(self, *args, **kwargs)
    return wrapper


def _no_op_callback(payload: InboundMessagePayload) -> None:
    pass


class Bot(ABC):
    def __init__(self):
        self._call_count = 0

    def dispatch_single_condition(
        self, payload: InboundMessagePayload,
        condition: ConditionFunction,
        on_satisfied_condition:  CallbackFunction= _no_op_callback,
        on_failed_condition: CallbackFunction = _no_op_callback
    ) -> bool:
        if condition(payload):
            on_satisfied_condition(payload)
            return True
        else:
            on_failed_condition(payload)
            return False

    def dispatch_many_conditions(
        self, payload: InboundMessagePayload,
        condition_callback_tuples: List[Tuple[ConditionFunction, CallbackFunction]]
    ) -> bool:
        for _condition, _callback in condition_callback_tuples:
            if self.dispatch_single_condition(payload, _condition, _callback, _no_op_callback):
                return True
        return False

    @abstractmethod
    def respond_to_message(self, payload: InboundMessagePayload):
        raise NotImplementedError("")
