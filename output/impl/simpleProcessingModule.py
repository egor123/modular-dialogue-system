import logging
from output.processing import ProcessingModuleBase
from wrappers import LLMWrapper
from container import Container

logger = logging.getLogger(__name__)

class SimpleProcessingModule(ProcessingModuleBase):
    def __init__(self, llm: LLMWrapper, history_limit: int = 5):
        self.llm = llm
        self.history_limit = history_limit

    def __build_prompt__(self, container: Container) -> str:
        if container.urgency >= 0.75:
            urgency_desc = "Respond quickly and decisively."
        elif container.urgency >= 0.5:
            urgency_desc = "Respond in a timely and calm manner."
        else:
            urgency_desc = "Take your time and respond thoughtfully."

        personality = ", ".join(container.personality) or "neutral"
        facts = " ".join(container.facts) or "No specific context."
        instructions = "\n".join(f"- {inst}" for inst in container.instructions) or "- No specific instructions."

        return f"""You are roleplaying a character with the following personality traits: **{personality}**.

Context to consider:
- **Known facts**: 
{facts}
- **Urgency**: {container.urgency:.2f} → {urgency_desc}

Your task:
- React naturally to the user's input.
- Follow the intent of the instructions below, but rephrase them in a natural, in-character way.
- Stay grounded in the provided facts and personality.
- Do not invent new actions or topics, only reword what's given.
- Do not add anything new
- Write small response

Conversation history:
{container.history[-self.history_limit:]}

User input:
"{container.input}"

Following intent of instruction below rephrase:
{instructions}

Your short response:"""

    def generate(self,  container: Container) -> str:
        prompt = self.__build_prompt__(container)
        logger.info(f"Generated prompt for LLM:\n{prompt}")
        response = self.llm.generate(prompt)
        if (response.startswith('"') and response.endswith('"')) or (response.startswith("'") and response.endswith("'")):
            return response[1:-1]
        return response