.. module:: gavel.dialects.base

Dialects
========

Parser
******

.. automodule:: gavel.dialects.base.parser
    :members:
    :private-members:

.. testsetup:: *

    from gavel.dialects.tptp.parser import TPTPParser, TPTPProblemParser

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


.. testcode::

    problem_parser = TPTPProblemParser()
    string = "cnf(a1, axiom, a | b).cnf(a1, axiom, ~a).cnf(a2, negated_conjecture, b)."

    for problem in problem_parser.parse(string):
        print("Axioms:")
        for a in problem.premises:
            print(a.formula)
        print("Conjecture:")
        print(problem.conjecture.formula)

.. testoutput::

    Axioms:
    (a) | (b)
    ~(a)
    Conjecture:
    b

Compiler
********

.. automodule:: gavel.dialects.base.compiler
    :members:
    :private-members:



.. automodule:: gavel.dialects.base.dialect
    :members:
    :private-members:
