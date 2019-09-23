from gavel.logic.logic import LogicElement
from typing import Iterable, List


class ProofStep:
    def __init__(self, name: str=None, **kwargs):
        self.name = name

class Inference(ProofStep):
    def __init__(self, antecedents: Iterable[ProofStep]=None, conclusion: LogicElement=None, **kwargs):
        super(Inference, self).__init__(**kwargs)
        self.antecedents = antecedents
        self.conclusion = conclusion


class Import(ProofStep):
    def __init__(self, element: LogicElement=None, source=None, **kwargs):
        super(Import, self).__init__(**kwargs)
        self.element = element
        self.source = source


class ProofGraph:
    def __init__(self, *args, premises: Iterable[LogicElement] = None, steps: List[ProofStep] = None, **kwargs):
        super(ProofGraph, self).__init__(*args, **kwargs)
        self.premises = premises
        self.steps = steps or []
        self._current_step = len(self.steps)
        self._step_dict = {s.name: s for s in self.steps}
        self.dependencies = {}



