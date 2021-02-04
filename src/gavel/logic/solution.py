from abc import ABC
from enum import Enum
from typing import Iterable
from typing import List
import graphviz as gv
from gavel.logic.logic import LogicElement
from gavel.logic import status


class ProofStep(ABC):
    def is_axiom(self):
        raise NotImplementedError


class IntroductionType(Enum):
    DEFINITION = 0
    AXIOM_OF_CHOICE = 1
    TAUTOLOGY = 2
    ASSUMPTION = 3


class Solution:
    def __init__(self, status: status.Status):
        self.status = status
        self.proof = None


class Proof:
    def __init__(
        self,
        *args,
        premises: Iterable[LogicElement] = None,
        steps: List[ProofStep] = None,
        status: status.Status,
        **kwargs
    ):
        super(Proof, self).__init__(*args, **kwargs)
        self.premises = premises or []
        self.steps = steps or []
        self.status = status
        self._used_axioms = None

    @property
    def used_axioms(self):
        if self._used_axioms is None:
            self._used_axioms = list(self._iterate_used_axioms())
        return self._used_axioms

    def _iterate_used_axioms(self):
        raise NotImplementedError

    def get_graph(self) -> gv.Digraph:
        g = gv.Digraph()
        labels = {}
        for s in self.steps:
            labels[s.name] = s.formula
            if isinstance(s, Inference):
                for a in s.antecedents:
                    g.edge(a, s.name, "Inference")
                shape = "oval"
            else:
                if isinstance(s, Introduction):
                    shape = "star"
                elif isinstance(s, Axiom):
                    shape = "box"
                else:
                    raise Exception(s)

            g.node(s.name, str(s.formula), shape=shape)
        return g


class LinearProof(Proof):
    def _iterate_used_axioms(self):
        return [step for step in self.steps if step.is_axiom()]
