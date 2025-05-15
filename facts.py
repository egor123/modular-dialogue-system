import logging
from typing import Any, Callable, Dict, List, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Fact(Generic[T]):
    def __init__(self, initial_value: T = None):
        self.value = initial_value
        self._callbacks_no_args: List[Callable[[], None]] = []
        self._callbacks_new_value: List[Callable[[T], None]] = []
        self._callbacks_old_new: List[Callable[[T, T], None]] = []

    def set(self, new_value: T):
        if new_value != self.value:
            old_value = self.value
            self.value = new_value
            logger.info(f"Fact updated: {old_value} -> {new_value}")
            self.__invoke_callbacks__(old_value, new_value)

    def get(self) -> T:
        return self.value

    def add_callback_no_args(self, callback: Callable[[], None]):
        self._callbacks_no_args.append(callback)

    def add_callback_new_value(self, callback: Callable[[T], None]):
        self._callbacks_new_value.append(callback)

    def add_callback_old_new(self, callback: Callable[[T, T], None]):
        self._callbacks_old_new.append(callback)

    def remove_callback_no_args(self, callback: Callable[[], None]):
        self._callbacks_no_args.remove(callback)

    def remove_callback_new_value(self, callback: Callable[[T], None]):
        self._callbacks_new_value.remove(callback)

    def remove_callback_old_new(self, callback: Callable[[T, T], None]):
        self._callbacks_old_new.remove(callback)

    def __invoke_callbacks__(self, old_value: T, new_value: T):
        for cb in self._callbacks_no_args:
            try:
                cb()
            except Exception as e:
                logger.error(f"Error in no-arg callback: {e}")
        for cb in self._callbacks_new_value:
            try:
                cb(new_value)
            except Exception as e:
                logger.error(f"Error in new-value callback: {e}")
        for cb in self._callbacks_old_new:
            try:
                cb(old_value, new_value)
            except Exception as e:
                logger.error(f"Error in old-new callback: {e}")


class FactSystem:
    def __init__(self):
        self._facts: Dict[str, Fact] = {}

    def set_fact(self, key: str, value: Any):
        if key not in self._facts:
            self._facts[key] = Fact(value)
        else:
            self._facts[key].set(value)

    def get_fact(self, key: str) -> Fact[Any]:
        if key in self._facts:
            return self._facts.get(key).get()
        else:
            fact = Fact()
            self._facts[key] = fact
            return fact