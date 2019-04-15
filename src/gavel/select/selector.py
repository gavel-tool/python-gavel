from itertools import chain
from typing import Iterable, Set, List
from gavel.logic.fol import AnnotatedFormula, FOLElement


class Selector:
    """
    Base class for gavel selectors.
    """

    def __init__(self, premises: List[AnnotatedFormula], conjecture: AnnotatedFormula):
        self.premises = premises
        self.conjecture = conjecture

    def select(self):
        return self.premises


class Sine(Selector):
    def __init__(
        self,
        premises: List[AnnotatedFormula],
        conjecture: AnnotatedFormula,
        tolerance: float,
        generality: int,
        max_depth: int = 5,
    ):
        super(Sine, self).__init__(premises, conjecture)
        self.symbols = set(
            chain(self.conjecture.symbols(), *(p.symbols() for p in premises))
        )
        self._premise_symbols = {p: set(p.symbols()) for p in self.premises}
        self.commonness = {
            s: sum(1 for ps in self._premise_symbols.values() if s in ps)
            for s in self.symbols
        }
        self.min_commonness = min(map(lambda x: self.commonness[x], self.symbols))
        self.tolerance = tolerance
        self.generality = generality
        self.max_depth = max_depth

    def select(self):
        return self.calculate_triggers().keys()

    def trigger(self, symbol, sentence: FOLElement) -> bool:
        return (
            symbol in sentence.symbols()
            and self.commonness[symbol] <= self.generality
            and self.commonness[symbol] <= self.tolerance * self.min_commonness
        )

    def calculate_triggers(self):
        premise_triggers = {p: 0 for p in self.premises}
        remaining_premises = list(self.premises)
        new_symbols = set()
        step = 0
        while new_symbols and step <= self.max_depth:
            step += 1
            temp_rem = []
            newer_symbols = set()
            for p in remaining_premises:
                p_symbs = self._premise_symbols[p]
                if any(self.trigger(s, p) for s in new_symbols):
                    newer_symbols = newer_symbols.union(p_symbs)
                    premise_triggers[p] = step
                else:
                    temp_rem.append(p)
            remaining_premises = temp_rem
            new_symbols = newer_symbols
        return premise_triggers
