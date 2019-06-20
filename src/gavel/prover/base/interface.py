from gavel.dialects.base.dialect import Problem, Dialect
from gavel.logic.base import LogicElement
from typing import Iterable


class BaseProverInterface:
    _dialect_cls = Dialect

    def __init__(self, *args, **kwargs):
        self.dialect = self._dialect_cls(*args, **kwargs)


    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """
        raise NotImplementedError

class BaseResultHandler:
    def get_used_axioms(self):
        raise NotImplementedError

