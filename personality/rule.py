import json
from dataclasses import dataclass
from condition import Condition
from events import EventSystem
from facts import FactSystem
from wrappers import EmbedderWrapper, ParaphraserWrapper, SentimentWrapper


@dataclass
class Rule:
    name: str
    template: str
    condition: Condition
    freedom: float = 0.5
    type: str = "insert"
    callback: str = ""

    @staticmethod
    def parse_rules(data: dict[str, any], embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, events: EventSystem, paraphrasings: int = 0) -> list:
        rules = []
        for name, rule_dict in data.items():
            rule = Rule(
                name=name,
                template=rule_dict["template"],
                freedom=rule_dict.get("freedom", 0.5),
                type=rule_dict.get("type", "insert"),
                condition=Condition(
                    rule_dict["condition"], embedder, sentiment, paraphraser, facts, paraphrasings),
                callback=rule_dict.get("callback", None)
            )
            rules.append(rule)

        return rules
