from typing import Iterable


class LogicElement:
    __visit_name__ = "undefined"

    requires_parens = False

    def symbols(self) -> Iterable:
        return []

class Sentence(LogicElement):
    def is_conjecture(self):
        raise NotImplementedError

class Problem:
    def __init__(
        self,
        premises: Iterable[Sentence],
        conjecture: Iterable[Sentence],
        imports=None,
    ):
        self.premises = premises
        self.conjecture = conjecture
        self.imports = imports or []
