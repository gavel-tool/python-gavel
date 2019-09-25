from typing import Iterable

from gavel.dialects.base.dialect import Compiler
from gavel.dialects.base.dialect import Dialect
from gavel.dialects.base.dialect import Problem
from gavel.logic.logic import LogicElement
from gavel.logic.proof import Proof


class BaseProverInterface:
    _prover_dialect_cls = Dialect

    def __init__(self, *args, **kwargs):
        super(BaseProverInterface, self).__init__(*args, **kwargs)
        self.dialect = self._prover_dialect_cls()

    def prove(self, problem: Problem, *args, **kwargs) -> Proof:
        return self._build_proof(
            self._post_process_proof(
                self._submit_problem(self._bootstrap_problem(problem))
            ),
            problem,
        )

    def _bootstrap_problem(self, problem: Problem):
        raise NotImplementedError

    def _submit_problem(self, problem_instance, *args, **kwargs):
        raise NotImplementedError

    def _post_process_proof(self, raw_proof_result):
        raise NotImplementedError

    def _build_proof(self, prover_output, problem: Problem) -> Proof:
        return self.dialect.parse_proof(prover_output)


class BaseResultHandler:
    def get_used_axioms(self):
        raise NotImplementedError
