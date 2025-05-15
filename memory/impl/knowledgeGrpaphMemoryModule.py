import logging
import json
import re
from facts import FactSystem
import loader
from container import Container
from memory.memory import MemoryModuleBase
from wrappers import ExtractionWrapper
logger = logging.getLogger(__name__)


class KnowledgeGrpaphMemoryModule(MemoryModuleBase):
    def __init__(self, file_path: str, extr: ExtractionWrapper, facts: FactSystem):
        self.extr = extr
        self.data = loader.load_config(file_path)
        self.facts: FactSystem = facts

    def __populate_facts__(self, container: Container):
        for t in [container.input, *container.instructions]:
            for entity in self.extr.extract_entities(t):
                return #FIXME
                for dict in self.data.items():
                    fact = dict.get(entity)
                    if fact != None:
                        container.facts.append(fact)

    def __insert_facts__(self, container: Container):
        pattern = re.compile(r'\$\{(.*?)\}')
        for i in range(len(container.instructions)):
            container.instructions[i] = pattern.sub(
                lambda match: self.__replace_fact__(match), container.instructions[i])

    def __replace_fact__(self, match) -> str:
        fact_name = match.group(1)
        fact = self.facts.get_fact(fact_name).get()
        return str(fact) if fact else ""

    def process(self, container: Container):
        self.__populate_facts__(container)
        self.__insert_facts__(container)
