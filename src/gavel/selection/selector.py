from itertools import chain
from typing import List, Dict

from gavel.logic.logic import LogicElement
from gavel.logic.problem import Problem


class Selector:
    """
    Base class for gavel selectors.
    """

    def select(self, problem: Problem, **kwargs) -> Problem:
        return problem


class Sine(Selector):
    def select(self, problem, max_depth=10):
        symbols = set(
            chain(
                problem.conjecture.symbols(), *(p.symbols() for p in problem.premises)
            )
        )
        premise_symbols = {p: set(p.symbols()) for p in problem.premises}
        commonness = {
            s: sum(1 for ps in premise_symbols.values() if s in ps) for s in symbols
        }

        return self.calculate_triggers(problem, premise_symbols, commonness, max_depth)

    def trigger(
        self, symbol, sentence: LogicElement, commonness: Dict[str, int]
    ) -> bool:
        return symbol in sentence.symbols() and all(
            commonness[symbol] <= commonness[symbol2] for symbol2 in sentence.symbols()
        )

    def calculate_triggers(
        self, problem: Problem, premise_symbols, commonness, max_depth
    ):
        remaining_premises = list(problem.premises)
        k_triggered_symbols = set(problem.conjecture.symbols())
        used_symbols = set()
        k = 0
        while k_triggered_symbols and k < max_depth:
            k += 1
            untriggered_premises = []
            newer_symbols = set()
            for p in remaining_premises:
                p_symbs = premise_symbols[p]
                # If s is k-step triggered and s triggers A, then A is k + 1-step triggered
                if any(self.trigger(s, p, commonness) for s in k_triggered_symbols):
                    newer_symbols = newer_symbols.union(p_symbs)
                    yield p
                else:
                    untriggered_premises.append(p)
            remaining_premises = untriggered_premises
            used_symbols = used_symbols.union(k_triggered_symbols)
            k_triggered_symbols = newer_symbols.difference(used_symbols)
