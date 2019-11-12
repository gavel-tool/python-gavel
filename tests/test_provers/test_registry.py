from unittest import TestCase
import pytest
from gavel.logic import logic
from gavel.prover.registry import register_prover, get_prover
from gavel.prover.base.interface import BaseProverInterface
from gavel.logic.proof import Proof, ProofStep


def simple_prover(problem):
    for premise in problem.premises:
        if premise.formula == problem.conjecture.formula:
            # Create a proof structure
            p = Proof(steps=[ProofStep(formula=premise.formula)])
            return p
    return None


@register_prover("test")
class TestProver(BaseProverInterface):
    def _submit_problem(self, problem_instance, *args, **kwargs):
        return Proof(
            premises=problem_instance.premises,
            steps=[
                ProofStep(
                    formula=logic.DefinedConstant.FALSUM,
                    name="name"
                )
            ],
        )


class TestSimpleProver(TestCase):
    def test_registry(self):
        self.assertEqual(get_prover("test"), TestProver)
