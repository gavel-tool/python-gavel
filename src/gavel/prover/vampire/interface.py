from gavel.dialects.base.dialect import Problem
from gavel.prover.base.interface import BaseProverInterface, BaseResultHandler
from gavel.dialects.tptp.dialect import TPTPDialect
import gavel.dialects.tptp.sources as sources

class VampireInterface(BaseProverInterface):
    _dialect_cls = TPTPDialect

    def prove(self, problem: Problem, *args, **kwargs):
        """
        Attempt to prove a problem specified in `file`
        :param file:
        :return:
        """

    def get_used_axioms(self, output):
        logic_parser = self.dialect._problem_parser_cls.logic_parser_cls()
        for goal in jsn["goals"]:
            for formula in logic_parser.load_many(
                goal["prover_output"].split("\n")):
                if isinstance(sources.FileSource, formula.annotation):
                    print(formula.annotation.info)


class ResultHandler(BaseResultHandler):
    def get_used_axioms(self):
        raise NotImplementedError
