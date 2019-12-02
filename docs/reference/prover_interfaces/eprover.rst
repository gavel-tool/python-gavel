.. module:: gavel.prover.eprover.interface
.. _eprover_interface:

Proving with EProver
====================

Install EProver according to "it's documentation":https://github.com/eprover/eprover and set the following environment variables:

* `EPROVER`: Path to your EProver binary

Now you can run gavel with the following command:

`eprover <problem_path>`

Python interface
----------------

The EProver interface does not take any Parameters:

.. testcode::

    from gavel.prover.eprover.interface import EProverInterface
    prover = EProverInterface()


.. autoclass:: EProverInterface
    :members:
