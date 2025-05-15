
from memory.memory import MemoryModuleBase
from preprocessing.preprocessor import PreprocessorBase
from flow.dialogue import DialogueFlowModuleBase
from personality.personality import PersonalityModuleBase
from output.processing import ProcessingModuleBase
import logging
from container import Container
logger = logging.getLogger(__name__)


class DialoguePipline:
    def __init__(self, preprocessor: PreprocessorBase, dialogue: DialogueFlowModuleBase, personality: PersonalityModuleBase, memory: MemoryModuleBase, processing: ProcessingModuleBase):
        self.preprocessor: PreprocessorBase = preprocessor
        self.dialogue: DialogueFlowModuleBase = dialogue
        self.personality: PersonalityModuleBase = personality
        self.processing: ProcessingModuleBase = processing
        self.memory: MemoryModuleBase = memory
        self.history: list[str] = []

    def evaluate(self, input: str) -> str:
        container = Container(input=input, history=self.history)
        self.preprocessor.process(container)
        self.dialogue.process(container)
        self.personality.process(container)
        self.memory.process(container)
        output = self.processing.generate(container)
        self.history.append(container.input)
        self.history.append(output)
        return output
