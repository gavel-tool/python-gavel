from gavel.prover.registry import register_prover
from gavel.dialects.base.dialect import Problem
from gavel.dialects.tptp.dialect import TPTPProofDialect
from gavel.dialects.tptp.parser import SimpleTPTPProofParser
from gavel.prover.base.interface import BaseProverInterface
from gavel.prover.base.interface import BaseResultHandler


class EDialect(TPTPProofDialect):
    def parse(self, obj, *args, **kwargs):
        cleaned_obj = "\n".join(line for line in obj.split("\n") if not line.startswith("#"))
        return super(EDialect, self).parse(cleaned_obj, *args, **kwargs)


@register_prover("eprover")
class EProverInterface(BaseProverInterface):
    _prover_dialect_cls = EDialect

    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """


class ResultHandler(BaseResultHandler):
    def get_used_axioms(self):
        raise NotImplementedError
