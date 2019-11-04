.. module:: gavel.dialects.base

Dialects
========

Parser
******

.. automodule:: gavel.dialects.base.parser
    :members:
    :private-members:

.. testsetup:: *

    from gavel.dialects.tptp.parser import TPTPParser

.. testcode::

    parser = TPTPParser()
    string = "cnf(name, axiom, a | b)."

    structure = parser.parse_single_from_string(string)
    print(structure.formula)

.. testoutput::

    (a) | (b)

.. testcode::

    parser = TPTPParser()
    string = "cnf(name, axiom, a | b).cnf(name, axiom, d | e)."

    for line in parser.stream_formula_lines(string):
        structure = parser.parse_single_from_string(line)
        print(structure.formula)

.. testoutput::

    (a) | (b)
    (d) | (e)

Compiler
********

.. automodule:: gavel.dialects.base.compiler
    :members:
    :private-members:



.. automodule:: gavel.dialects.base.dialect
    :members:
    :private-members:
