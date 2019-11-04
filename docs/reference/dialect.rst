.. module:: gavel.dialects.base

Dialects
========

Parser
******


Gavel comes with a collection of parsers for different logical frameworks. You can use these parsers to parse a
single expression from a string:

.. testcode::

    from gavel.dialects.tptp.parser import TPTPParser

    parser = TPTPParser()
    string = "cnf(name, axiom, a | b)."

    structure = parser.parse_single_from_string(string)
    print(structure.formula)

.. testoutput::

    (a) | (b)

In most cases the exact structrue of the input is not known, e.g. it might contain several expressions. To extract all
lines from a string use the `parse_single_from_string` which returns a generator of found expressions

.. testcode::

    string = "cnf(name, axiom, a | b).cnf(name, axiom, d | e)."

    for line in parser.stream_formula_lines(string):
        structure = parser.parse_single_from_string(line)
        print(structure.formula)

.. testoutput::

    (a) | (b)
    (d) | (e)

If you want to parse a complete problem from a file, use the specific problem parser. As some reasoners (e.g. SPASS) do
not accept problems that cotain multiple conjectures, :class:`ProblemParser.parse` returns a generator of problems,
containing one conjecture each.

.. testcode::

    from gavel.dialects.tptp.parser import TPTPProblemParser

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


.. automodule:: gavel.dialects.base.parser
    :members:
    :private-members:


Compiler
********

.. automodule:: gavel.dialects.base.compiler
    :members:
    :private-members:



.. automodule:: gavel.dialects.base.dialect
    :members:
    :private-members:
