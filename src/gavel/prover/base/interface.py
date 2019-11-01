from typing import Iterable

from gavel.dialects.base.dialect import Compiler
from gavel.dialects.base.dialect import Dialect, IdentityDialect
from gavel.dialects.base.dialect import Problem
from gavel.logic.logic import LogicElement
from gavel.logic.proof import Proof


class BaseProverInterface:
    """
    Base class for prover support
    """
    _prover_dialect_cls = IdentityDialect

    def __init__(self, *args, **kwargs):
        super(BaseProverInterface, self).__init__(*args, **kwargs)
        self.dialect = self._prover_dialect_cls()

    def prove(self, problem: Problem, *args, **kwargs) -> Proof:
        return self.build_proof(
            self._post_process_proof(
                self._submit_problem(self._bootstrap_problem(problem))
            ),
            problem,
        )

    def _bootstrap_problem(self, problem: Problem):
        """
        Transforms the given `problem` into a format that is understood
        by this prover.

        Parameters
        ----------

        problem
            A problem instance

        Returns
        -------

        A problem format that is understood by the prover
        """
        return self.dialect.compile_problem(problem)

    def _submit_problem(self, problem_instance, *args, **kwargs):
        """
        Expects a problem in a format that is supported by the prover,
        submits this problem to the prover and receives the result.

        Parameters
        ----------

        problem_instance
            A problem

        Returns
        -------

        The proof result the format used by the prover
        """
        raise NotImplementedError

    def _post_process_proof(self, raw_proof_result):
        """
        Apply some transformation to make the output of the prover processabe
        by `_prover_dialect_cls`

        Parameters
        ----------
        raw_proof_result

        Returns
        -------
        """

        return raw_proof_result

    def build_proof(self, prover_output, problem: Problem) -> Proof:
        """
        Parses the proof returned by the prover.

        Parameters
        ----------
        prover_output
            Prover output in a parseable format
        problem

        Returns
        -------
            A proof object
        """
        return self.dialect.parse_proof(prover_output)


class BaseResultHandler:
    def get_used_axioms(self):
        raise NotImplementedError
