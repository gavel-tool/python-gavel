from gavel.dialects.tptp.parser import TPTPParser, TPTPProblemParser
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.logic import logic
from gavel.logic import problem
from ..test_base.test_parser import TestLogicParser, check_wrapper, TestProblemParser
from gavel.config.settings import TPTP_ROOT
import os
import unittest
import multiprocessing as mp
from unittest import skip


class TestTPTPParser(TestLogicParser):
    _parser_cls = TPTPParser

    def test_verum(self):
        inp = """fof(mElmSort,axiom,(
    ! [W0] :
      ( aElement0(W0)
     => $true ) ))."""
        result = problem.AnnotatedFormula(
            logic="fof",
            name="mElmSort",
            role=problem.FormulaRole.AXIOM,
            formula=logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable("W0")],
                formula=logic.BinaryFormula(
                    left=logic.PredicateExpression(
                        predicate="aElement0", arguments=[logic.Variable("W0")]
                    ),
                    operator=logic.BinaryConnective.IMPLICATION,
                    right=logic.DefinedConstant.VERUM,
                ),
            ),
        )
        self.check_parser(inp, result)

    def test_functor(self):
        inp = """cnf(and_definition1,axiom,( and(X,n0) = n0 ))."""
        result = problem.AnnotatedFormula(
            logic="cnf",
            name="and_definition1",
            role=problem.FormulaRole.AXIOM,
            formula=logic.BinaryFormula(
                left=logic.FunctorExpression(
                    functor="and", arguments=[logic.Variable("X"), logic.Constant("n0")]
                ),
                operator=logic.BinaryConnective.EQ,
                right=logic.Constant("n0"),
            ),
        )
        self.check_parser(inp, result)

    @check_wrapper()
    def test_single_quote(self):
        inp = "p('This is arbitrary text')"
        result = logic.PredicateExpression(
            "p", [logic.Constant("'This is arbitrary text'")]
        )
        return inp, result

    @check_wrapper()
    def test_double_quote(self):
        inp = 'p("This is arbitrary text")'
        result = logic.PredicateExpression(
            "p", [logic.DistinctObject('"This is arbitrary text"')]
        )
        return inp, result

    @check_wrapper()
    def test_quantifier(self):
        inp = "![X1,X2]:?[Y1,Y2]:p(X1,X2,Y1,Y2)"
        result = logic.QuantifiedFormula(
            logic.Quantifier.UNIVERSAL,
            [logic.Variable("X1"), logic.Variable("X2")],
            logic.QuantifiedFormula(
                logic.Quantifier.EXISTENTIAL,
                [logic.Variable("Y1"), logic.Variable("Y2")],
                logic.PredicateExpression(
                    "p",
                    [
                        logic.Variable("X1"),
                        logic.Variable("X2"),
                        logic.Variable("Y1"),
                        logic.Variable("Y2"),
                    ],
                ),
            ),
        )
        return inp, result


class TestTPTPProblemParser(TestProblemParser):
    _parser_cls = TPTPProblemParser

    def test_problems_1(self):
        inp = """fof(a1, axiom, p(a) => q(a)).
fof(a2, axiom, q(a) => $false).
fof(a3, axiom, $true => p(a)).
fof(c, conjecture, $false)."""
        result = [
            problem.Problem(
                premises=[
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a1",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="q", arguments=[logic.Constant("a")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a2",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="q", arguments=[logic.Constant("a")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a3",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.DefinedConstant.VERUM,
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                        ),
                    ),
                ],
                conjecture=problem.AnnotatedFormula(
                    logic="fof",
                    name="c",
                    role=problem.FormulaRole.CONJECTURE,
                    formula=logic.DefinedConstant.FALSUM,
                ),
            )
        ]

        self.check_parser(inp, result)

    def test_problems_2(self):
        inp = """fof(a1, axiom, (p(a) & p(b) & p(d)) => $false).
fof(a2, axiom, p(e)  => $false).
fof(a3, axiom, p(c) => p(a)).
fof(a4, axiom, p(c)   => $false).
fof(a5, axiom, p(a) => p(d)).
fof(c, conjecture, $false)."""
        result = [
            problem.Problem(
                premises=[
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a1",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.BinaryFormula(
                                left=logic.PredicateExpression(
                                    predicate="p", arguments=[logic.Constant("a")]
                                ),
                                operator=logic.BinaryConnective.CONJUNCTION,
                                right=logic.BinaryFormula(
                                    left=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("b")]
                                    ),
                                    operator=logic.BinaryConnective.CONJUNCTION,
                                    right=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("d")]
                                    ),
                                ),
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a2",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("e")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a3",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a4",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a5",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("d")]
                            ),
                        ),
                    ),
                ],
                conjecture=problem.AnnotatedFormula(
                    logic="fof",
                    name="c",
                    role=problem.FormulaRole.CONJECTURE,
                    formula=logic.DefinedConstant.FALSUM,
                ),
            )
        ]
        self.check_parser(inp, result)

    def test_problems_3(self):
        inp = """fof(a1, axiom, (p(e) & p(b) & p(d)) => $false).
fof(a2, axiom, p(e) => p(d)).
fof(a3, axiom, $true => p(f)).
fof(a4, axiom, p(a) => $false).
fof(a5, axiom, p(c) => p(e)).
fof(a6, axiom, $true => p(c)).
fof(c, conjecture, $false)."""
        result = [
            problem.Problem(
                premises=[
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a1",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.BinaryFormula(
                                left=logic.PredicateExpression(
                                    predicate="p", arguments=[logic.Constant("e")]
                                ),
                                operator=logic.BinaryConnective.CONJUNCTION,
                                right=logic.BinaryFormula(
                                    left=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("b")]
                                    ),
                                    operator=logic.BinaryConnective.CONJUNCTION,
                                    right=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("d")]
                                    ),
                                ),
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a2",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("e")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("d")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a3",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.DefinedConstant.VERUM,
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("f")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a4",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a5",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("e")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a6",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.DefinedConstant.VERUM,
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                        ),
                    ),
                ],
                conjecture=problem.AnnotatedFormula(
                    logic="fof",
                    name="c",
                    role=problem.FormulaRole.CONJECTURE,
                    formula=logic.DefinedConstant.FALSUM,
                ),
            )
        ]
        self.check_parser(inp, result)


    def test_problems_4(self):
        inp = """fof(a1, axiom, (p(e) & p(b) & p(d)) => $false).
fof(a2, axiom, p(e) => p(d)).
fof(a3, axiom, $true => p(b)).
fof(a4, axiom, p(a) => $false).
fof(a5, axiom, p(c) => p(e)).
fof(a6, axiom, $true => p(c)).
fof(c, conjecture, $false)."""
        result = [
            problem.Problem(
                premises=[
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a1",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.BinaryFormula(
                                left=logic.PredicateExpression(
                                    predicate="p", arguments=[logic.Constant("e")]
                                ),
                                operator=logic.BinaryConnective.CONJUNCTION,
                                right=logic.BinaryFormula(
                                    left=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("b")]
                                    ),
                                    operator=logic.BinaryConnective.CONJUNCTION,
                                    right=logic.PredicateExpression(
                                        predicate="p", arguments=[logic.Constant("d")]
                                    ),
                                ),
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a2",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("e")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("d")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a3",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.DefinedConstant.VERUM,
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("b")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a4",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("a")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.DefinedConstant.FALSUM,
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a5",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("e")]
                            ),
                        ),
                    ),
                    problem.AnnotatedFormula(
                        logic="fof",
                        name="a6",
                        role=problem.FormulaRole.AXIOM,
                        formula=logic.BinaryFormula(
                            left=logic.DefinedConstant.VERUM,
                            operator=logic.BinaryConnective.IMPLICATION,
                            right=logic.PredicateExpression(
                                predicate="p", arguments=[logic.Constant("c")]
                            ),
                        ),
                    ),
                ],
                conjecture=problem.AnnotatedFormula(
                    logic="fof",
                    name="c",
                    role=problem.FormulaRole.CONJECTURE,
                    formula=logic.DefinedConstant.FALSUM,
                ),
            )
        ]
        self.check_parser(inp, result)


"""
class TestTHFParser(TestLogicParser):
    _parser_cls = TPTPParser

    @skip
    def test_type_formula(self):
        inp = "thf(prop_a,type,(
    prop_a: $i > $o ))."
        expected = problem.AnnotatedFormula(
            logic="thf",
            name="prop_a",
            role=problem.FormulaRole.TYPE,
            formula=logic.TypeFormula(
                name=logic.Constant("prop_a"),
                type_expression=logic.MappingType(
                    left="$i",
                    right="$o"
                )
            )
        )
        self.check_parser(inp, expected)
"""
