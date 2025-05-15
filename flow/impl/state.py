import logging
from facts import FactSystem
from flow.impl.transition import Transition
from wrappers import EmbedderWrapper, ParaphraserWrapper, SentimentWrapper

logger = logging.getLogger(__name__)

class State:
    def __init__(self, urgency: float, freedom: float, name: str, template: str, transitions: list['Transition'], on_enter: str, on_exit: str):
        self.urgency: float = urgency
        self.freedom: float = freedom
        self.template: str = template
        self.name: str = name
        self.transitions: list[Transition] = transitions
        self.on_enter: str = on_enter
        self.on_exit: str = on_exit

    @staticmethod
    def from_dict(name: str, data: dict, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, paraphrasings: int = 0):
        urgency = data.get('urgency', 0.5)
        freedom = data.get('freedom', 0.5)
        template = data.get('template', '')
        transitions = [
            Transition.from_dict(t, embedder, sentiment, paraphraser, facts, paraphrasings)
            for t in data.get('transitions', [])
        ]
        on_enter = data.get('on_enter', None)
        on_exit = data.get('on_exit', None)
        return State(name=name, urgency=urgency, freedom=freedom, template=template, transitions=transitions, on_enter=on_enter, on_exit=on_exit)