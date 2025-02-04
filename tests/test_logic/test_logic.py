import unittest
from gavel.logic import logic


class TestEquality(unittest.TestCase):
    """Syntactic equality (with symmetry) between gavel formulas"""

    def test_predicate(self):
        v1 = logic.Variable("v1")
        v3 = logic.Constant("v3")
        f1 = logic.PredicateExpression("abc", [v1, v3])
        f2 = logic.PredicateExpression("abc", [v1, v3])
        f3 = logic.PredicateExpression("abc", [v1, logic.Constant("v4")])
        f4 = logic.PredicateExpression("abc", [v1])
        f5 = logic.PredicateExpression("def", [v1, v3])
        self.assertEqual(f1, f2)
        self.assertNotEqual(f1, f3)
        self.assertNotEqual(f1, f4)
        self.assertNotEqual(f1, f5)

    def test_symmetric_conj(self):
        v1 = logic.Variable("v1")
        v3 = logic.Constant("v3")
        formulae = [logic.PredicateExpression("abc", [v1, v3]),
                    logic.PredicateExpression("def", [v3, v1, v1]),
                    logic.UnaryFormula(logic.UnaryConnective.NEGATION, logic.PredicateExpression("abc", [v1, v1]))]
        f1 = logic.BinaryFormula(formulae[0], logic.BinaryConnective.CONJUNCTION, formulae[1])
        f2 = logic.BinaryFormula(formulae[1], logic.BinaryConnective.CONJUNCTION, formulae[0])
        f3 = logic.BinaryFormula(formulae[0], logic.BinaryConnective.DISJUNCTION, formulae[1])
        f4 = logic.BinaryFormula(formulae[2], logic.BinaryConnective.CONJUNCTION, formulae[1])
        self.assertEqual(f1, f2)
        self.assertNotEqual(f1, f3)
        self.assertNotEqual(f1, f4)


class TestNaryFormula(unittest.TestCase):
    def test_nary_conjunction(self):
        triformula = logic.NaryFormula(
            logic.BinaryConnective.CONJUNCTION,
            [logic.PredicateExpression("c", [logic.Constant("atom1")]),
             logic.PredicateExpression("n", [logic.Constant("atom2")]),
             logic.BinaryFormula(logic.PredicateExpression("h", [logic.Constant("atom3")]),
                                 logic.BinaryConnective.DISJUNCTION,
                                 logic.PredicateExpression("c", [logic.Constant("atom3")]))])
        self.assertTrue(triformula.is_valid())

    def test_nary_implication(self):
        # should fail, implications have to be binary
        with self.assertRaises(AssertionError):
            logic.NaryFormula(
                logic.BinaryConnective.IMPLICATION,
                [logic.PredicateExpression("c", [logic.Constant("atom1")]),
                 logic.PredicateExpression("n", [logic.Constant("atom2")]),
                 logic.BinaryFormula(
                     logic.PredicateExpression("h", [logic.Constant("atom3")]),
                     logic.BinaryConnective.DISJUNCTION,
                     logic.PredicateExpression("c", [logic.Constant("atom3")]))])


class TestOperatorOverloading(unittest.TestCase):

    def test_negation(self):
        formula = logic.PredicateExpression("abc", [logic.Variable("x")])
        negated_formula = logic.UnaryFormula(logic.UnaryConnective.NEGATION, formula)
        self.assertEqual(negated_formula, ~formula)

    def test_conjunction_disjunction(self):
        p1 = logic.PredicateExpression("abc", [logic.Variable("x")])
        p2 = logic.PredicateExpression("def", [logic.Variable("y")])
        p3 = logic.PredicateExpression("ghi", [logic.Variable("z")])
        formula = logic.BinaryFormula(
            p1, logic.BinaryConnective.CONJUNCTION,
            logic.BinaryFormula(p2, logic.BinaryConnective.DISJUNCTION, p3))
        self.assertEqual(formula, p1 & (p2 | p3))


if __name__ == '__main__':
    unittest.main()
