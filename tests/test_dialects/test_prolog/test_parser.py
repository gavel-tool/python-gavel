from gavel.dialects.prolog.parser import PrologParser
from gavel.logic import logic
from gavel.logic.problem import AnnotatedFormula, FormulaRole
from tests.test_dialects.test_base.test_parser import TestLogicParser

class TestPrologParser(TestLogicParser):
    _parser_cls = PrologParser

    def test_parse_fact(self):
        prolog_program = """
        father(tom, bob).
        """
        inp = prolog_program

        result = AnnotatedFormula(
            logic="fol",
            name="fact_1",
            role=FormulaRole.AXIOM,
            formula=logic.PredicateExpression(
                predicate="father",
                arguments=[
                    logic.Constant("tom"),
                    logic.Constant("bob")
                ]
            )
        )

        self.check_parser(inp, [result])

    def test_parse_rule(self):
        prolog_program = """
        parent(X, Y) :- father(X, Y).
        """
        inp = prolog_program
        result = AnnotatedFormula(
            logic="fol",
            name="rule_1",
            role=FormulaRole.AXIOM,
            formula=logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable("X"), logic.Variable("Y")],
                formula=logic.BinaryFormula(
                    left=logic.PredicateExpression(
                        predicate="father",
                        arguments=[
                            logic.Variable("X"),
                            logic.Variable("Y")
                        ]
                    ),
                    operator=logic.BinaryConnective.IMPLICATION,
                    right=logic.PredicateExpression(
                        predicate="parent",
                        arguments=[
                            logic.Variable("X"),
                            logic.Variable("Y")
                        ]
                    )
                )
            )
        )
        self.check_parser(inp, [result])

    def test_parse_query(self):
        prolog_program = """
        ?- parent(tom, bob).
        """
        inp = prolog_program
        result = AnnotatedFormula(
            logic="fol",
            name="query_1",
            role=FormulaRole.CONJECTURE,
            formula=logic.PredicateExpression(
                predicate="parent",
                arguments=[
                    logic.Constant("tom"),
                    logic.Constant("bob")
                ]
            )
        )
        self.check_parser(inp, [result])