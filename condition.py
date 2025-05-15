import numbers
import logging
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import re
from facts import FactSystem
from wrappers import EmbedderWrapper, SentimentWrapper, ParaphraserWrapper

logger = logging.getLogger(__name__)


class Condition():
    def __init__(self, expr: str, embedder: EmbedderWrapper, sentiment: SentimentWrapper, paraphraser: ParaphraserWrapper, facts: FactSystem, paraphrasings: int = 0):
        logger.info(f"Parsing condition: {expr}")
        self.embedder = embedder
        self.sentiment = sentiment
        self.paraphraser = paraphraser
        self.paraphrasings = paraphrasings
        self.facts = facts
        self.tokens = self.__tokenize__(expr)
        logger.info(f"tokens: {self.tokens}")
        self.position = 0
        self.expr = self.__parse__()

    def __tokenize__(self, expr: str):
        tokens_map = [
            ('NUMBER',  r"\d+(\.\d*)?"),
            ('SIM',     r"sim\('.*?'\)"),
            ('SENT',    r"sent\('.*?'\)"),
            ('FACT',    r"fact\('.*?'\)"),
            ('AND',     r"\band\b"),
            ('OR',      r"\bor\b"),
            ('OP',      r"<=|>=|==|<|>"),
            ('LPAREN',  r"\("),
            ('RPAREN',  r"\)"),
            ('SKIP',    r"[ \t]+"),
        ]
        regex = '|'.join('(?P<%s>%s)' % pair for pair in tokens_map)
        pattern = re.compile(regex)
        pos = 0
        tokens = []
        while pos < len(expr):
            match = pattern.match(expr, pos)
            if not match:
                raise SyntaxError(
                    f"Unexpected character at {pos}: {expr[pos]}")
            (type, value, pos) = (match.lastgroup, match.group(), match.end())
            if type != 'SKIP':
                tokens.append((type, value))
        return tokens

    # --- PARSER ---
    def __peek__(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else (None, None)

    def __advance__(self):
        tok = self.__peek__()
        self.position += 1
        return tok

    def __parse__(self):
        return self._parse_or()

    def _parse_or(self):
        node = self._parse_and()
        while self.__peek__()[1] == 'or':
            self.__advance__()
            right = self._parse_and()
            node = self.OrEvaluator(node, right)
        return node

    def _parse_and(self):
        node = self._parse_comparison()
        while self.__peek__()[1] == 'and':
            self.__advance__()
            right = self._parse_comparison()
            node = self.AndEvaluator(node, right)
        return node

    def _parse_comparison(self):
        node = self._parse_primary()
        while self.__peek__()[0] == 'OP':
            op = self.__advance__()[1]
            right = self._parse_primary()
            node = self.OperatorEvaluator(node, right, op)
        return node

    def _parse_primary(self):
        tok_type, tok_val = self.__peek__()
        if tok_type == 'LPAREN':
            self.__advance__()
            node = self.__parse__()
            if self.__peek__()[0] != 'RPAREN':
                raise SyntaxError("Missing closing parenthesis")
            self.__advance__()
            return node
        elif tok_type == 'SIM':
            self.__advance__()
            arg = re.match(r"sim\('(.*?)'\)", tok_val).group(1)
            args = [arg]
            if self.paraphrasings > 0:
                args += self.paraphraser.paraphrase(self.paraphrasings, arg)
            return self.SimilarityEvaluator(args, self.embedder)
        elif tok_type == 'SENT':
            self.__advance__()
            arg = re.match(r"sent\('(.*?)'\)", tok_val).group(1)
            return self.SentimentEvaluator(arg, self.sentiment)
        elif tok_type == 'FACT':
            self.__advance__()
            arg = re.match(r"fact\('(.*?)'\)", tok_val).group(1)
            return self.FactEvaluator(arg, self.facts)
        elif tok_type == 'NUMBER':
            self.__advance__()
            return self.NumericEvaluator(float(tok_val))
        else:
            raise SyntaxError(f"Unexpected token: {tok_val}")

    # --------------- Evaluation -------------

    def eval(self, input: str) -> float:
        return self.expr.eval(input)

    class Evaluator(ABC):
        @abstractmethod
        def eval(self, input: str) -> float:
            pass

    class OperatorEvaluator(Evaluator):
        def __init__(self, ev1, ev2, operator: str):
            self.ev1 = ev1
            self.ev2 = ev2
            self.operator = operator

        def eval(self, input: str) -> float:
            match self.operator:
                case ">":
                    return int(self.ev1.eval(input) > self.ev2.eval(input))
                case ">=":
                    return int(self.ev1.eval(input) >= self.ev2.eval(input))
                case "<":
                    return int(self.ev1.eval(input) < self.ev2.eval(input))
                case "<=":
                    return int(self.ev1.eval(input) <= self.ev2.eval(input))
                case "==":
                    return int(self.ev1.eval(input) <= self.ev2.eval(input))

    class NumericEvaluator(Evaluator):
        def __init__(self, value: float):
            self.value = value

        def eval(self, input: str) -> float:
            return self.value

    class OrEvaluator(Evaluator):
        def __init__(self, ev1, ev2):
            self.ev1 = ev1
            self.ev2 = ev2

        def eval(self, input: str) -> float:
            return max(self.ev1.eval(input), self.ev2.eval(input))

    class AndEvaluator(Evaluator):
        def __init__(self, ev1, ev2):
            self.ev1 = ev1
            self.ev2 = ev2

        def eval(self, input: str) -> float:
            return min(self.ev1.eval(input), self.ev2.eval(input))

    class SimilarityEvaluator(Evaluator):
        def __init__(self, args: list[str], embedder: EmbedderWrapper):
            self.embedder = embedder
            self.arg_embeddings = [embedder.encode(arg) for arg in args]

        def eval(self, input: str) -> float:
            input_embedding = self.embedder.encode(input)
            max_score = 0
            for embedding in self.arg_embeddings:
                similarity = util.cos_sim(input_embedding, embedding)[0][0]
                max_score = max(max_score, similarity.item())
            logger.info(f"Similarity evaluation: {max_score}")
            return max_score

    class SentimentEvaluator(Evaluator):
        def __init__(self, arg: str, sentiment: SentimentWrapper):
            self.label = arg
            self.sentiment = sentiment

        def eval(self, input: str) -> float:
            data = self.sentiment.encode(input)
            logger.info(f"Sentimental evaluation: {data}")
            if data["label"] == self.label.upper():
                return data["score"]
            return 0  # 1 - data["score"]

    class FactEvaluator(Evaluator):
        def __init__(self, arg: str, facts: FactSystem):
            self.arg = arg
            self.facts = facts
        
        def eval(self, input: str) -> float:
            value = self.facts.get_fact(self.arg).get()
            if value == None:
                return 0
            if isinstance(value, numbers.Number):
                return float(value)
            if isinstance(value, bool):
                return 1 if value else 0  
            return 1

# if __name__ == "__main__":
#     sentiment = pipeline("sentiment-analysis")
#     embedder = SentenceTransformer("stsb-roberta-large")
#     embedderWrapper = EmbedderWrapper(
#         lambda arg: embedder.encode(arg, convert_to_tensor=True))
#     sentimentWrapper = SentimentWrapper(lambda arg: sentiment(arg)[0])
#     condition = Condition(
#         "sim('greetings') and sent('positive')", embedderWrapper, sentimentWrapper)
#     print(condition.eval("hello, how it's going?"))
