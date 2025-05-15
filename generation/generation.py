import logging
from abc import ABC, abstractmethod
from container import Container

logger = logging.getLogger(__name__)


class GenerationModuleBase(ABC):
    @abstractmethod
    def generate(container: Container) -> str:
        pass
