from gavel.prover.registry import register_prover
from gavel.dialects.base.dialect import Problem
from gavel.dialects.tptp.dialect import TPTPProblemDialect
from gavel.prover.base.interface import BaseProverInterface
from gavel.prover.base.interface import BaseResultHandler


@register_prover("vampire")
class VampireInterface(BaseProverInterface):
    _prover_dialect_cls = TPTPProblemDialect

    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """


class ResultHandler(BaseResultHandler):
    def get_used_axioms(self):
        raise NotImplementedError
