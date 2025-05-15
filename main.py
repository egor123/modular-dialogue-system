import tkinter as tk
import logging
import spacy
import torch
from sentence_transformers import SentenceTransformer
from chat import ChatApp
from preprocessing.impl.simplePreprocessor import SimplePreprocessor
from langchain_ollama.llms import OllamaLLM
from flow.impl.fsmDialogueFlowModule import FSMDialogueFlowModule
from wrappers import SummarizationWrapper, EmbedderWrapper, SentimentWrapper, ExtractionWrapper, LLMWrapper, ParaphraserWrapper
from personality.impl.simplePersonalityModule import SimplePersonalityModule
from memory.impl.knowledgeGrpaphMemoryModule import KnowledgeGrpaphMemoryModule
from generation.impl.simpleProcessingModule import SimpleProcessingModule
from pipeline import DialoguePipline
from transformers import pipeline
from facts import FactSystem
from events import EventSystem
logger = logging.getLogger(__name__)

def config():
    logger.info("Initializing...")

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    summarizer = pipeline(
        "summarization", model="facebook/bart-large-cnn", device=device)
    summarizerWrapper = SummarizationWrapper(lambda txt, min, max: summarizer(
        txt, min_length=min, max_length=max, do_sample=False)[0]['summary_text'])
    embedder = SentenceTransformer("stsb-roberta-large", device=device)
    embedderWrapper = EmbedderWrapper(
        lambda arg: embedder.encode(arg, convert_to_tensor=True))
    sentiment = pipeline(
        "sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis", device=device)
    sentimentWrapper = SentimentWrapper(lambda arg: sentiment(arg)[0])
    nlp = spacy.load("en_core_web_sm")
    extrWrapper = ExtractionWrapper(
        lambda txt: [ent.text for ent in nlp(txt).ents])
    llm = OllamaLLM(model="llama3")
    paraphraserWrapper = ParaphraserWrapper(lambda n, t: llm.invoke(
        (
            f"Give me {n} different natural sentences to say: '{t}'.\n"
            "List them, one per line. Do not write anything else"
        )
    )[0]['generated_text'].split("\n"))
    llmWrapper = LLMWrapper(lambda prompt: llm.invoke(prompt))

    events = EventSystem()
    facts = FactSystem()

    preprocessor = SimplePreprocessor(summarizerWrapper)
    flowModule = FSMDialogueFlowModule(
        "example_configs/fsm_dialogue.json", embedderWrapper, sentimentWrapper, paraphraserWrapper, facts, events)
    personalityModule = SimplePersonalityModule(
        "example_configs/rule_personality.json", embedderWrapper, sentimentWrapper, paraphraserWrapper, facts, events)
    memoryModule = KnowledgeGrpaphMemoryModule(
        "example_configs/graph_world_state.json", extrWrapper, facts)
    processingModule = SimpleProcessingModule(llmWrapper)
    dialogue_pipeline = DialoguePipline(
        preprocessor, flowModule, personalityModule, memoryModule, processingModule)
    logger.info("Initialization is finished")
    return dialogue_pipeline


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # ERROR
    use_gui = True

    dialogue_pipeline = config()

    if use_gui:
        root = tk.Tk()
        app = ChatApp(root, dialogue_pipeline)
        root.mainloop()
    else:
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break
                print(dialogue_pipeline.evaluate(user_input))

            except KeyboardInterrupt:
                print('Interrupted')
                break
