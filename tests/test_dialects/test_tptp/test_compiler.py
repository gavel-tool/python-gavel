import unittest

from gavel.logic import logic

from src.gavel.dialects.tptp.compiler import TPTPCompiler
from ..test_base.test_compiler import TestCompiler


class TestTPTPCompiler(TestCompiler):
    compiler = TPTPCompiler

    def test_variable(self):
        self.assert_compiler(logic.Variable("X"), "X")

    def test_connective(self):
        for input_conn, expected_conn in [
            (logic.BinaryConnective.CONJUNCTION, "&"),
            (logic.BinaryConnective.DISJUNCTION, "|"),
        ]:
            with self.subTest(input_conn=input_conn, expected_conn=expected_conn):
                self.assert_compiler(
                    logic.BinaryFormula(
                        logic.Variable("X"), input_conn, logic.Variable("Y")
                    ),
                    "X%sY" % expected_conn,
                )

    def test_predicate_names_starting_with_digits(self):
        self.assert_compiler(
            logic.PredicateExpression("123/test", [logic.Variable("X"), logic.Variable("Y")]),
            "'123_test(X,Y)'",
        )

    def test_constant_names_starting_with_underscores(self):
        self.assert_compiler(
            logic.PredicateExpression("http___example_org_hasAncestor", [logic.Constant("http___example_org_Mary"), logic.Constant("__genid2147483649")]),
            "'http___example_org_hasAncestor'('http___example_org_Mary','__genid2147483649')",
        )

