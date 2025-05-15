from typing import Callable
from torch import Tensor


class SummarizationWrapper():
    def __init__(self, func: Callable[[str, int, int], str]):
        self.func = func

    def summarize(self, text: str, min_len: int, max_len: int) -> str:
        return self.func(text, min_len, max_len)


class EmbedderWrapper():
    def __init__(self, func: Callable[[str], Tensor]):
        self.func = func

    def encode(self, arg: str) -> Tensor:
        return self.func(arg)


class SentimentWrapper():
    def __init__(self, func: Callable[[str], dict]):
        self.func = func

    def encode(self, arg: str) -> dict:
        return self.func(arg)


class ExtractionWrapper():
    def __init__(self, func: Callable[[str], list[str]]):
        self.func = func

    def extract_entities(self, text: str) -> list[str]:
        return self.func(text)


class ParaphraserWrapper():
    def __init__(self, func: Callable[[int, str], list[str]]):
        self.func = func
    def paraphrase(self, num: int, text: str) -> list[str]:
        return self.func(num, text)

class LLMWrapper():
    def __init__(self, func: Callable[[str], str]):
        self.func = func

    def generate(self, text: str) -> str:
        return self.func(text)
