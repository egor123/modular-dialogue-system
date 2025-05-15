import logging
from abc import ABC, abstractmethod
from container import Container
logger = logging.getLogger(__name__)


class DialogueFlowModuleBase(ABC):
    @abstractmethod
    def process(self, container: Container):
        pass
