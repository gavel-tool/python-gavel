from typing import Iterable


class LogicElement:
    __visit_name__ = "undefined"

    requires_parens = False

    def symbols(self) -> Iterable:
        return []
