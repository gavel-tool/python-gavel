from typing import Iterable

from gavel.dialects.base.dialect import Dialect
from gavel.dialects.base.dialect import Problem
from gavel.dialects.base.dialect import Compiler
from gavel.prover.base.proof_structures import ProofGraph
from gavel.logic.logic import LogicElement


class BaseProverInterface:
    _prover_dialect_cls = Dialect

    def __init__(self, *args, **kwargs):
        super(BaseProverInterface, self).__init__(*args, **kwargs)
        self.dialect = self._prover_dialect_cls()

    def prove(self, problem: Problem, *args, **kwargs) -> ProofGraph:
        return self._build_proof_graph(self._post_process_proof(
            self._submit_problem(self._bootstrap_problem(problem))), problem
        )

    def _bootstrap_problem(self, problem: Problem):
        raise NotImplementedError

    def _submit_problem(self, problem_instance, *args, **kwargs):
        raise NotImplementedError

    def _post_process_proof(self, raw_proof_result):
        raise NotImplementedError

    def _build_proof_graph(self, lines: Iterable[LogicElement], problem: Problem) -> ProofGraph:
        raise NotImplementedError

class BaseResultHandler:
    def get_used_axioms(self):
        raise NotImplementedError
