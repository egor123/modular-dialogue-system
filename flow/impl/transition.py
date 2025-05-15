import logging
from condition import Condition
from facts import FactSystem
from wrappers import EmbedderWrapper, ParaphraserWrapper, SentimentWrapper

logger = logging.getLogger(__name__)


class Transition:
    def __init__(self, urgency: float, freedom: float, to: str, template: str, evaluator: Condition, on_enter: str):
        self.urgency: float = urgency
        self.freedom: float = freedom
        self.to: str = to
        self.template: str = template
        self.evaluator: Condition = evaluator
        self.on_enter: str = on_enter

    @staticmethod
    def from_dict(data: dict, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, paraphrasings: int = 0):
        return Transition(
            urgency=data.get('urgency', 0.5),
            freedom=data.get('freedom', 0),
            to=data.get('to', None),
            template=data.get('template', ''),
            evaluator=Condition(data.get('condition', ''),
                                embedder, sentiment, paraphraser, facts, paraphrasings),
            on_enter=data.get('on_exit', ''),
        )
