from typing import Iterable


class LogicElement:
    __visit_name__ = "undefined"

    requires_parens = False

    def symbols(self) -> Iterable:
        return []


class Problem:
    def __init__(
        self,
        premises: Iterable[LogicElement],
        conjecture: Iterable[LogicElement],
        imports=None,
    ):
        self.premises = premises
        self.conjecture = conjecture
        self.imports = imports or []
