.. module:: gavel.prover.hets.interface
.. _hets_interface:

Proving with Hets
#################



Online
------

In order to use the online version run `gavel` with the following environment variables:

  * `HETS_HOST`: rest.hets.eu
  * `HETS_PORT`: 80

following options parameters:

`eprover --hets <problem_path>`

Offline
-------

Follow the instructions in the "hets documentation":https://github.com/spechub/Hets and start `hets --server` **or**
run "the docker container":https://github.com/spechub/Hets/wiki/How-to-use-the-Hets-Docker-Container
(the mount option is not necessary as gavel uses the rest interface instead of shared files).

  * `HETS_HOST`: localhost
  * `HETS_PORT`: The port your docker container is forwarding

following options parameters:

`eprover --hets <problem_path>`

Python interface
----------------

Hets is just a layer around a number of provers. The latest version of gavel only supports
EProver. In order to use any Proverinterface with hets, you have to pass it to the constructor:

.. testcode::
    from gavel.prover.base.interface import BaseProverInterface
    internal_prover = BaseProverInterface() # Or any subclass or anything that quacks like ProverInterface
    hets_engine = HetsEngine()
    hets_session = HetsSession(hets_engine)
    prover = HetsProve(internal_prover)

.. autoclass:: HetsEngine
    :members:

.. autoclass:: HetsSession
    :members:

.. autoclass:: HetsProve
    :members:
