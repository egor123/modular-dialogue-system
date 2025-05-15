import logging
from transformers import pipeline
from preprocessing.preprocessor import PreprocessorBase
from wrappers import SummarizationWrapper
from container import Container
logger = logging.getLogger(__name__)


class SimplePreprocessor(PreprocessorBase):
    def __init__(self, summarizer: SummarizationWrapper, min_input_len: int = 10, max_input_len: int = 15):
        self.min_input_len = min_input_len
        self.max_input_len = max_input_len
        self.summarizer = summarizer

    def process(self, container: Container) -> str:
        word_count = len(container.input.split())
        if word_count > self.max_input_len:
            container.input = self.summarizer.summarize(
                container.input, self.min_input_len, self.max_input_len)
        logger.info(f"Proccessed input: {container.input}")


if __name__ == "__main__":
    tests = [
        """
Yes, I would be happy to help you on this quest! I'm always ready to assist with something as noble as this.
It sounds dangerous, but count me in.
""",
        """
No, I will not do this quest
"""
    ]
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    wrapper = SummarizationWrapper(lambda txt, min, max: summarizer(
        txt, min_length=min, max_length=max, do_sample=False)[0]['summary_text'])
    # print(wrapper.summarize(tests[0], 10, 15))
    preprocessor = SimplePreprocessor(wrapper)
    for test in tests:
        print(f"Processing\n{test}\n{preprocessor.process(test)}")
