import logging
from facts import FactSystem
from events import EventSystem
import loader
from flow.impl.state import State
from flow.impl.transition import Transition
from flow.dialogue import DialogueFlowModuleBase
from wrappers import EmbedderWrapper, ParaphraserWrapper, SentimentWrapper
from container import Container

logger = logging.getLogger(__name__)


class FSMDialogueFlowModule(DialogueFlowModuleBase):
    def __init__(self, config_file: str, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, events: EventSystem, threshold: float = 0.4, min_diff=0.1, paraphrasings: int = 0):
        self.state_machine = loader.load_config(config_file)
        self.threshold = threshold
        self.min_diff = min_diff
        self.events = events
        self.states: dict[str, State] = {}
        for name, state in self.state_machine['states'].items():
            state['name'] = name
            self.states[name] = State.from_dict(
                name, state, embedder, sentiment, paraphraser, facts, paraphrasings)
        logger.info(f"Loaded states: {self.states}")
        self.current_state = self.state_machine.get(
            "initial_state", next(iter(self.states.keys())))
        logger.info(f"Start state: {self.current_state}")        

    def get_state(self) -> State:
        return self.states[self.current_state]

    def process(self, container: Container):
        state = self.get_state()
        transitions = [(t.to, t.evaluator.eval(container.input), t)
                       for t in state.transitions]
        transitions = sorted(transitions, key=lambda x: x[1], reverse=True)
        logger.info(f"Possible transitions: {transitions}")
        transition: tuple[str, float, Transition] = None
        if len(transitions) > 0 and transitions[0][1] > self.threshold:
            if len(transitions) >= 2:
                if transitions[0][1] - transitions[1][1] > self.min_diff:
                    transition = transitions[0]
            else:
                transition = transitions[0]
        if transition is None:
            logger.info("No transitions found")
            container.freedom = state.freedom
            container.urgency = state.urgency
            container.instructions.append(state.template)
        else:
            logger.info(f"Transition to: {transition}")
            self.events.invoke(self.get_state().on_exit)
            self.current_state = transition[0]
            container.freedom = transition[2].freedom
            container.urgency = transition[2].urgency
            self.events.invoke(transition[2].on_enter)
            container.instructions.append(transition[2].template)
            container.instructions.append(self.get_state().template)
            self.events.invoke(self.get_state().on_enter)
