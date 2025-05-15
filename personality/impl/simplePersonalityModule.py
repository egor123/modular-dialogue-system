import logging
from facts import FactSystem
from events import EventSystem
from wrappers import EmbedderWrapper, SentimentWrapper, ParaphraserWrapper
from personality.personality import PersonalityModuleBase
from container import Container
from personality.rule import Rule
import loader

logger = logging.getLogger(__name__)


class SimplePersonalityModule(PersonalityModuleBase):
    def __init__(self, config_file: str, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, events: EventSystem, paraphrasings: int = 0, default_threshold: float = 0.8):
        conf = loader.load_config(config_file)
        self.default_threshold = default_threshold
        self.description = conf.get("description", "")
        self.rules: list[Rule] = Rule.parse_rules(
            conf.get("rules", []), embedder, sentiment, paraphraser, facts, paraphrasings)
        self.events = events

    def __apply_rules__(self, container: Container):
        for rule in self.rules:
            if rule.freedom >= container.freedom:
                val = rule.condition.eval(container.input) 
                logger.info(val)
                if val >= self.default_threshold:
                    if rule.type == "overwrite":
                        logger.info(f"All instructions are owerwritten to: '{rule.template}': {val}")
                        container.instructions = [rule.template]
                    else:
                        logger.info(f"Instruction is inserted: '{rule.template}': {val}")
                        container.instructions.append(rule.template)

    def process(self, container: Container):
        container.personality.append(self.description)
        self.__apply_rules__(container)
