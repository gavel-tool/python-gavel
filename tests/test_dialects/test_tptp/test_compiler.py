import unittest

from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.logic import logic

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
