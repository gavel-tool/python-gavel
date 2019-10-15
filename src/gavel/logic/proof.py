from abc import ABC
from enum import Enum
from typing import Iterable
from typing import List
import graphviz as gv
from gavel.logic.logic import LogicElement
from gavel.logic.problem import FormulaRole


class ProofStep(ABC):
    def __init__(self, formula: LogicElement = None, name: str = None, **kwargs):
        self.name = name
        self.formula = formula

    def is_axiom(self):
        return False

    def render_source(self):
        raise NotImplementedError


class Axiom(ProofStep):
    def is_axiom(self):
        return True

    def render_source(self):
        return "axiom"


class IntroductionType(Enum):
    DEFINITION = 0
    AXIOM_OF_CHOICE = 1
    TAUTOLOGY = 2
    ASSUMPTION = 3


class Inference(ProofStep):
    def __init__(
        self,
        antecedents: Iterable[ProofStep] = None,
        conclusion: LogicElement = None,
        **kwargs
    ):
        super(Inference, self).__init__(**kwargs)
        self.antecedents = antecedents

    def render_source(self):
        return " :- " + ", ".join(a for a in self.antecedents)


class Introduction(ProofStep):
    def __init__(self, introduction_type: IntroductionType = None, **kwargs):
        super(Introduction, self).__init__(**kwargs)
        self.type = introduction_type

    def render_source(self):
        return self.type.name.lower()


class Proof:
    def __init__(
        self,
        *args,
        premises: Iterable[LogicElement] = None,
        steps: List[ProofStep] = None,
        **kwargs
    ):
        self.premises = premises or []
        self.steps = steps or []
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
        return [step for step in self.steps if step.role == FormulaRole.AXIOM]
