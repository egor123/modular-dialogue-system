from typing import Callable, Dict, List
import logging
logger = logging.getLogger(__name__)


class EventSystem:
    def __init__(self):
        self.events: Dict[str, List[Callable[[], None]]] = {}

    def add_evt(self, evt_name: str, action: Callable[[], None]):
        if evt_name not in self.events:
            self.events[evt_name] = []
        if action not in self.events[evt_name]:
            self.events[evt_name].append(action)
            logger.debug(f"Added action to event '{evt_name}'")
        else:
            logger.debug(f"Action already registered to event '{evt_name}'")

    def remove_evt(self, evt_name: str, action: Callable[[], None]):
        if evt_name in self.events and action in self.events[evt_name]:
            self.events[evt_name].remove(action)
            logger.debug(f"Removed action from event '{evt_name}'")
            if not self.events[evt_name]:
                del self.events[evt_name]
                logger.debug(
                    f"Removed event '{evt_name}' as it has no more actions")

    def invoke(self, evt_name: str):
        if evt_name == None or evt_name == '':
            return
        logger.info(f"Event invoked: '{evt_name}'")
        if evt_name in self.events:
            for action in self.events[evt_name]:
                try:
                    action()
                except Exception as e:
                    logger.error(
                        f"Error invoking action for event '{evt_name}': {e}")