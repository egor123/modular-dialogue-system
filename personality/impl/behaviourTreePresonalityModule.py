import logging
from facts import FactSystem
from events import EventSystem
from wrappers import EmbedderWrapper, SentimentWrapper, ParaphraserWrapper
from personality.personality import PersonalityModuleBase
from container import Container
from abc import ABC, abstractmethod
from condition import Condition
import loader

logger = logging.getLogger(__name__)


class BTNode(ABC):
    @abstractmethod
    def run(self, container) -> bool:
        pass

    @staticmethod
    def from_dict(data, embedder, sentiment, paraphraser, facts, events, paraphrasings):
        node_type = data["type"]
        if node_type == "sequence":
            return SequenceNode([BTNode.from_dict(child, embedder, sentiment, paraphraser, facts, events, paraphrasings) for child in data["children"]])
        elif node_type == "selector":
            return SelectorNode([BTNode.from_dict(child, embedder, sentiment, paraphraser, facts, events, paraphrasings) for child in data["children"]])
        elif node_type == "condition":
            condition = Condition(data["condition"], embedder, sentiment, paraphraser, facts, paraphrasings)
            return ConditionNode(condition)
        elif node_type == "action":
            return ActionNode(data["template"], data["callback"], data.get("mode", "append"), events)
        else:
            raise ValueError(f"Unknown node type: {node_type}")


class SequenceNode(BTNode):
    def __init__(self, children: list[BTNode]):
        self.children = children

    def run(self, container) -> bool:
        for child in self.children:
            if not child.run(container):
                return False
        return True


class SelectorNode(BTNode):
    def __init__(self, children: list[BTNode]):
        self.children = children

    def run(self, container) -> bool:
        for child in self.children:
            if child.run(container):
                return True
        return False


class ConditionNode(BTNode):
    def __init__(self, condition):
        self.condition = condition

    def run(self, container) -> bool:
        return self.condition.eval(container.input)


class ActionNode(BTNode):
    def __init__(self, template: str, callback: str, mode: str, events):
        self.template = template
        self.callback = callback
        self.mode = mode
        self.events = events

    def run(self, container) -> bool:
        self.events.invoke(self.callback)
        if self.mode == "overwrite":
            container.instructions = [self.template]
        else:
            container.instructions.append(self.template)
        return True

class BehaviorTreePersonalityModule(PersonalityModuleBase):
    def __init__(self, config_file: str, embedder: EmbedderWrapper, sentiment: SentimentWrapper,
                 paraphraser: ParaphraserWrapper, facts: FactSystem, events: EventSystem, paraphrasings: int = 0):
        conf = loader.load_config(config_file)
        self.description = conf.get("description", "")
        self.events = events

        self.root: BTNode = BTNode.from_dict(conf["behavior_tree"], embedder, sentiment, paraphraser, facts, events, paraphrasings)

    def process(self, container: Container):
        container.personality.append(self.description)
        result = self.root.run(container)
        logger.info(f"Behavior tree result: {result}")