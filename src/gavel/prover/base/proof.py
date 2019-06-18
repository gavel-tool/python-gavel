from gavel.dialects.base.dialect import Problem
from gavel.logic.base import LogicElement
from typing import Iterable

class ProverInterface:
    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """


class ProofElement:
    __visitor_name__ = None

    def get_used_premises(self):
        raise NotImplementedError


class Inference(ProofElement):
    def __init__(self, antecedent: Iterable[LogicElement], conclusion: LogicElement):
        self.antecedent = antecedent
        self.conclusion = conclusion


