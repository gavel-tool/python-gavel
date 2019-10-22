from gavel.dialects.tptp.parser import TPTPParser, TPTPAntlrParser
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.logic import logic
from gavel.logic import problem
from ..test_base.test_parser import TestLogicParser, check_wrapper
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
        result = logic.PredicateExpression("p",[logic.Constant("'This is arbitrary text'")])
        return inp,result

    @check_wrapper()
    def test_double_quote(self):
        inp = "p(\"This is arbitrary text\")"
        result = logic.PredicateExpression("p",[logic.DistinctObject("\"This is arbitrary text\"")])
        return inp,result

    @check_wrapper()
    def test_quantifier(self):
        inp = "![X1,X2]:?[Y1,Y2]:p(X1,X2,Y1,Y2)"
        result = logic.QuantifiedFormula(
            logic.Quantifier.UNIVERSAL,
            [logic.Variable("X1"), logic.Variable("X2")],
            logic.QuantifiedFormula(
                logic.Quantifier.EXISTENTIAL,
                [logic.Variable("Y1"), logic.Variable("Y2")],
                logic.PredicateExpression("p", [logic.Variable("X1"), logic.Variable("X2"),logic.Variable("Y1"), logic.Variable("Y2")])
            )
        )
        return inp, result

@skip
class TestLALRSanity(TestTPTPParser):
    def __init__(self, *args, **kwargs):
        super(TestLALRSanity, self).__init__(*args, **kwargs)
        self.antlr_parser = TPTPAntlrParser()

    def test_formula(self):
        f = 'fof(maps,axiom,( ! [F,A,B] :( ' \
            'maps(F,A,B)' \
            '<=> ' \
            '(' \
            '   ! [X] :( ' \
            '       member(X,A)' \
        '           => ' \
            '       ? [Y] :( ' \
            '           member(Y,B)' \
            '           & ' \
            '           apply(F,X,Y) ' \
            '       ) ' \
            '   )' \
            '   & ' \
            '   ! [X,Y1,Y2] :( ' \
            '       ( ' \
            '           member(X,A)' \
            '           & ' \
            '           member(Y1,B)' \
            '           & ' \
            '           member(Y2,B)' \
            '       )' \
            '       => ' \
            '       ( ' \
            '           (' \
            '               apply(F,X,Y1)' \
            '               &' \
            '               apply(F,X,Y2)' \
            '           )' \
            '           => ' \
            '               Y1 ' \
            '               = ' \
            '               Y2 ' \
            '      ) ' \
            '   ) ' \
            ') ) )).'
        self.assertObjectEqual(self.parser.parse_single_from_string(f),
                               self.antlr_parser.parse_single_from_string(f))

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
