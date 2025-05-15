import logging
from typing import List, Dict, Optional
from facts import FactSystem
from events import EventSystem
from container import Container
from flow.dialogue import DialogueFlowModuleBase
from wrappers import EmbedderWrapper, ParaphraserWrapper, SentimentWrapper
from condition import Condition
import loader

logger = logging.getLogger(__name__)

class Action:
    def __init__(self, name, preconditions, effects, template, evaluator, on_success=None, on_fail=None):
        self.name = name
        self.preconditions: List[Condition] = preconditions
        self.effects: List[str] = effects
        self.template = template
        self.evaluator = evaluator
        self.on_success = on_success
        self.on_fail = on_fail

    @staticmethod
    def from_dict(data, embedder, sentiment, paraphraser, facts, paraphrasings = 0):
        return Action(
            name=data['name'],
            preconditions = [Condition(p,
                                embedder, sentiment, paraphraser, facts, paraphrasings) for p in data.get('preconditions', [])],
            effects=data.get('effects', []),
            template=data.get('template', ""),
            evaluator=Condition(data.get('condition', ''),
                                embedder, sentiment, paraphraser, facts, paraphrasings),
            on_success=data.get('on_success'),
            on_fail=data.get('on_fail'),
        )

    def is_applicable(self) -> bool:
        return all(p.eval('') for p in self.preconditions)

    def apply_effects(self, events: EventSystem):
        for e in self.effects:
            events.invoke(e)

    def execute(self, container: Container, events: EventSystem) -> bool:
        if self.evaluator.eval(container.input):
            self.apply_effects(events)
            return True
        return False

class GOAPPlanner:
    def __init__(self, actions: Dict[str, Action]):
        self.actions = actions

    def plan(self, facts: FactSystem, goal: dict) -> Optional[List[Action]]:
        plan = []
        state = {k: facts.get_fact(k) for k in goal.keys()}

        while not self._goal_met(state, goal):
            applicable = [a for a in self.actions.values() if a.is_applicable()]
            if not applicable:
                return None

            action = applicable[0]
            plan.append(action)
            for k, v in action.effects.items():
                state[k] = v
        return plan

    def _goal_met(self, state: dict, goal: dict) -> bool:
        return all(state.get(k) == v for k, v in goal.items())


class GOAPDialogueFlowModule(DialogueFlowModuleBase):
    def __init__(self, config_file: str, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, events: EventSystem):
        self.config = loader.load_config(config_file)
        self.facts = facts
        self.events = events
        self.actions: Dict[str, Action] = {}

        for name, action_data in self.config['actions'].items():
            action_data['name'] = name
            self.actions[name] = Action.from_dict(
                action_data, embedder, sentiment, paraphraser, facts)

        self.goal = self.config["goal"]
        self.planner = GOAPPlanner(self.actions)
        self.current_plan: Optional[List[Action]] = []
        logger.info(f"GOAP system initialized with {len(self.actions)} actions and goal: {self.goal}")

    def process(self, container: Container):
        if not self.current_plan:
            logger.info("Planning new goal path...")
            self.current_plan = self.planner.plan(self.facts, self.goal)
            if not self.current_plan:
                logger.warning("Planning failed. No valid path to goal.")
                container.instructions.append("I can't help you right now.")
                return

        current_action = self.current_plan[0]
        logger.info(f"Executing action: {current_action.name}")

        try:
            success = current_action.execute(container, self.events)
        except Exception as e:
            logger.error(f"Action '{current_action.name}' failed with error: {e}")
            success = False

        if success:
            logger.info(f"Action '{current_action.name}' succeeded.")
            self.events.invoke(current_action.on_success)
            self.current_plan.pop(0)
            container.instructions.append(current_action.template)
        else:
            logger.warning(f"Action '{current_action.name}' failed. Replanning...")
            self.events.invoke(current_action.on_fail)
            self.current_plan = self.planner.plan(self.facts, self.goal)

        if not self.current_plan:
            logger.info("Goal achieved or no further actions.")