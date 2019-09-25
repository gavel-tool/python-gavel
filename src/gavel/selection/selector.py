from itertools import chain
from typing import List

from gavel.logic.logic import LogicElement
from gavel.logic.problem import AnnotatedFormula


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
        self.max_depth = max_depth

    def select(self):
        return self.calculate_triggers()

    def trigger(self, symbol, sentence: LogicElement) -> bool:
        return symbol in sentence.symbols() and all(
            self.commonness[symbol] <= self.commonness[symbol2]
            for symbol2 in sentence.symbols()
        )

    def calculate_triggers(self):
        remaining_premises = list(self.premises)
        k_triggered_symbols = set(self.conjecture.symbols())
        used_symbols = set()
        k = 0
        while k_triggered_symbols and k < self.max_depth:
            k += 1
            untriggered_premises = []
            newer_symbols = set()
            for p in remaining_premises:
                p_symbs = self._premise_symbols[p]
                # If s is k-step triggered and s triggers A, then A is k + 1-step triggered
                if any(self.trigger(s, p) for s in k_triggered_symbols):
                    newer_symbols = newer_symbols.union(p_symbs)
                    yield p
                else:
                    untriggered_premises.append(p)
            remaining_premises = untriggered_premises
            used_symbols = used_symbols.union(k_triggered_symbols)
            k_triggered_symbols = newer_symbols.difference(used_symbols)


class SineTolerance(Sine):
    def __init__(self, *args, tolerance, **kwargs):
        super(SineTolerance, self).__init__(*args, **kwargs)
        self.tolerance = tolerance

    def trigger(self, symbol, sentence: LogicElement) -> bool:
        return symbol in sentence.symbols() and all(
            self.commonness[symbol] <= self.tolerance * self.commonness[symbol2]
            for symbol2 in sentence.symbols()
        )


class SineGenerality(Sine):
    def __init__(self, *args, generality, **kwargs):
        super(SineGenerality, self).__init__(*args, **kwargs)
        self.generality = generality

    def trigger(self, symbol, sentence: LogicElement) -> bool:
        return (
            symbol in sentence.symbols()
            and self.commonness[symbol] <= self.generality
            and all(
                self.commonness[symbol] <= self.commonness[symbol2]
                for symbol2 in sentence.symbols()
            )
        )
