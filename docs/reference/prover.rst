.. module:: gavel.prover.base.interface

Provers
=======

Gavel is designed to support a number of provers. The communication to those is handled by so called prover interfaces
(see :class:`BaseProverInterface`).

.. autoclass:: BaseProverInterface
    :members:

    .. autoproperty:: _prover_dialect_cls

Custom Provers
**************

The following example
defines a rudimentary parser that checks whether the conjecture is part
of the premises - without any semantic insight.

.. testsetup:: *

    from gavel.prover.base.interface import BaseProverInterface
    from gavel.prover.registry import register_prover, get_prover
    from gavel.logic import problem as prob
    from gavel.logic import logic
    from gavel.logic.proof import Proof, ProofStep

.. testcode::

    def simple_prover(problem):
        for premise in problem.premises:
            if premise.formula == problem.conjecture.formula:
                # Create a proof structure
                p = Proof(steps=[ProofStep(formula=premise.formula)])
                return p
        return None

We can use this prover to prove really simple problems:

.. testcode::

    problem = prob.Problem(
        premises=[prob.AnnotatedFormula(logic="fof", name="axiom1", role=prob.FormulaRole.AXIOM, formula=logic.DefinedConstant.VERUM)],
        conjecture=prob.AnnotatedFormula(logic="fof", name="conjecture", role=prob.FormulaRole.CONJECTURE, formula=logic.DefinedConstant.VERUM)
    )
    proof = simple_prover(problem)
    for step in proof.steps:
        print(step.formula)

.. testoutput::

    $true

If you want to use your own prover in gavel, you need to implement
in a prover interface. Simply implement a subclass of
:class:`BaseProverInterface`.

.. testcode::

    class YourProverInterface(BaseProverInterface):
        def _submit_problem(self, problem_instance, *args, **kwargs):
            # Call your prov:qer here
            result = simple_prover(problem_instance)
            return result

.. testcode::

    pi = YourProverInterface()
    proof = pi.prove(problem)
    for step in proof.steps:
        print(step.formula)

.. testoutput::

    $true


Note that `simple_prover` is accepting and returning the structures used by gavel. If your parser requires a different
format, you may want to implement a dialect and use it in :class:`YourProverInterface._prover_dialect_cls`.
