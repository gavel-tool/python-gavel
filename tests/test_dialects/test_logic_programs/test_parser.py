from gavel.dialects.logic_programs.parser import LogicProgramParser
from gavel.logic import logic
from gavel.logic.problem import AnnotatedFormula, FormulaRole
from tests.test_dialects.test_base.test_parser import TestLogicParser

class TestLogicProgramParser(TestLogicParser):
    _parser_cls = LogicProgramParser

    def test_parse_fact(self):
        logic_program = """
        father(tom, bob).
        """
        inp = logic_program

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
        logic_program = """
        parent(X, Y) :- father(X, Y).
        """
        inp = logic_program
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
        logic_program = """
        ?- parent(tom, bob).
        """
        inp = logic_program
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

    def test_parse_inequality(self):
        logic_program = """
        unequal(X, Y) :- X != Y.
        """
        inp = logic_program
        result = AnnotatedFormula(
            logic="fol",
            name="rule_1",
            role=FormulaRole.AXIOM,
            formula=logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable("X"), logic.Variable("Y")],
                formula=logic.BinaryFormula(
                    left=logic.BinaryFormula(
                        left=logic.Variable("X"),
                        operator=logic.BinaryConnective.NEQ,
                        right=logic.Variable("Y")
                    ),
                    operator=logic.BinaryConnective.IMPLICATION,
                    right=logic.PredicateExpression(
                        predicate="unequal",
                        arguments=[
                            logic.Variable("X"),
                            logic.Variable("Y")
                        ]
                    )
                )
            )
        )
        self.check_parser(inp, [result])

    def test_negation(self):
        logic_program = """
        uncyclic(X, Y) :- not cyclic(X, Y).
        """
        inp = logic_program
        result = AnnotatedFormula(
            logic="fol",
            name="rule_1",
            role=FormulaRole.AXIOM,
            formula=logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable("X"), logic.Variable("Y")],
                formula=logic.BinaryFormula(
                    left=logic.UnaryFormula(
                        connective=logic.UnaryConnective.NEGATION,
                        formula=logic.PredicateExpression(
                            predicate="cyclic",
                            arguments=[
                                logic.Variable("X"),
                                logic.Variable("Y")
                            ]
                        )
                    ),
                    operator=logic.BinaryConnective.IMPLICATION,
                    right=logic.PredicateExpression(
                        predicate="uncyclic",
                        arguments=[
                            logic.Variable("X"),
                            logic.Variable("Y")
                        ]
                    )
                )
            )
        )
        self.check_parser(inp, [result])