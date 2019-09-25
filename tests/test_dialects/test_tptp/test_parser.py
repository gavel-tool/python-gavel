from gavel.dialects.tptp.parser import TPTPParser
from gavel.logic import logic
from gavel.logic import problem

from ..test_base.test_parser import TestLogicParser


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
                    left=logic.FunctorExpression(
                        functor="aElement0", arguments=[logic.Variable("W0")]
                    ),
                    operator=logic.BinaryConnective.IMPLICATION,
                    right=logic.DefinedConstant.VERUM,
                ),
            ),
        )
        self.check_parser(inp, result)
