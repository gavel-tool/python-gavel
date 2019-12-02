.. module:: gavel.selection.selector

Select Premises
===============

As theorem proving is very computationally expensive, you may want to select
premises that are beneficial to proof the given conjecture. Note that an exhaustive
proof but unsuccessful attempt does not yield any information about the whole problem.

.. testsetup::

    from gavel.prover.eprover.interface import EProverInterface
    prover = EProverInterface()
    prover.prove = lambda x: x
    problem = None

.. testcode::

    from gavel.selection.selector import Selector
    selector = Selector()
    small_problem = selector.select(problem)
    prover.prove(small_problem)

.. autoclass:: Selector
    :members:

