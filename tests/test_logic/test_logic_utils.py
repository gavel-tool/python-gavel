import unittest
from gavel.logic import logic, logic_utils


class TestFormulaUtils(unittest.TestCase):
    def test_get_vars_in_formula(self):
        formula = logic.NaryFormula(
            logic.BinaryConnective.CONJUNCTION,
            [logic.PredicateExpression("c", [logic.Variable("x")]),
             logic.PredicateExpression("n", [logic.Constant("atom2")]),
             logic.BinaryFormula(logic.PredicateExpression("h", [logic.Constant("k"), logic.Variable("z")]),
                                 logic.BinaryConnective.DISJUNCTION,
                                 logic.PredicateExpression("c", [logic.Variable("x")]))])
        variables = logic_utils.get_vars_in_formula(formula)
        self.assertTrue(logic.Variable("x") in variables)
        self.assertFalse(logic.Variable("k") in variables)  # k is a constant
        self.assertTrue(logic.Variable("z") in variables)

    def test_flatten_formula(self):
        # ((abc & def) & ((ghi & (abc & def) & (ghi | jkl))))
        formula = logic.BinaryFormula(
            logic.BinaryFormula(
                logic.PredicateExpression("abc", [logic.Variable("x")]),
                logic.BinaryConnective.CONJUNCTION,
                logic.PredicateExpression("def", [logic.Variable("y")])
            ),
            logic.BinaryConnective.CONJUNCTION,
            logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, [
                logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, [
                    logic.PredicateExpression("ghi", [logic.Constant("a")])
                ]),
                logic.BinaryFormula(
                    logic.PredicateExpression("abc", [logic.Variable("x")]),
                    logic.BinaryConnective.CONJUNCTION,
                    logic.PredicateExpression("def", [logic.Variable("y")])
                ),
                logic.NaryFormula(logic.BinaryConnective.DISJUNCTION, [
                    logic.PredicateExpression("ghi", [logic.Constant("a")]),
                    logic.PredicateExpression("jkl", [logic.Constant("b")])
                ])
            ])
        )
        # result should be a n-ary formula
        self.assertTrue(isinstance(logic_utils.binary_to_nary(formula, logic.BinaryConnective.CONJUNCTION), logic.NaryFormula))
        # formula should not have conjunctions in layer below
        self.assertFalse(any(isinstance(f, logic.BinaryFormula)
                             or (isinstance(f, logic.NaryFormula) and f.operator == logic.BinaryConnective.CONJUNCTION)
                             for f in logic_utils.binary_to_nary(formula, logic.BinaryConnective.CONJUNCTION).formulae))
        # don't flatten disjunction
        self.assertTrue(any(isinstance(f, logic.NaryFormula) and f.operator == logic.BinaryConnective.DISJUNCTION
                        for f in logic_utils.binary_to_nary(formula, logic.BinaryConnective.CONJUNCTION).formulae))

    def test_substitute_var_in_formula(self):
        for formula in [logic.PredicateExpression("abc", [logic.Variable("X"), logic.Variable("Y")]),
                        logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, [
                            logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, [
                                logic.PredicateExpression("ghi", [logic.Variable("X")])
                            ]),
                            logic.BinaryFormula(
                                logic.PredicateExpression("abc", [logic.Variable("X")]),
                                logic.BinaryConnective.CONJUNCTION,
                                logic.PredicateExpression("def", [logic.Variable("Y")])
                            ),
                            logic.NaryFormula(logic.BinaryConnective.DISJUNCTION, [
                                logic.PredicateExpression("ghi", [logic.Constant("a")]),
                                logic.PredicateExpression("jkl", [logic.Variable("X")])
                            ])
                        ])]:
            new_constant = logic.Constant("c1")
            substituted = logic_utils.substitute_var_in_formula(formula, logic.Variable("X"), new_constant)
            self.assertFalse(logic.Variable("X") in logic_utils.get_vars_in_formula(substituted))
            self.assertTrue("c1" in substituted.symbols())
            (self.assertTrue(logic.Variable("Y") in logic_utils.get_vars_in_formula(substituted),
                             f"Found only variables "
                             f"{[str(var) for var in logic_utils.get_vars_in_formula(substituted)]}"
                             f" in formula {substituted}"))

    def test_operator_overloading(self):
        formula = logic.PredicateExpression("abc", [logic.Constant("m")])
        negated_formula = ~formula
        self.assertTrue(isinstance(negated_formula, logic.UnaryFormula))
        self.assertEqual(str(negated_formula), str(logic.UnaryFormula(logic.UnaryConnective.NEGATION, formula)))

    def testNNF(self):
        formula_eq = logic.UnaryFormula(
            logic.UnaryConnective.NEGATION,
            logic.BinaryFormula(logic.Variable("x"), logic.BinaryConnective.EQ, logic.Variable("y")))

        formula_biimp = logic.UnaryFormula(
            logic.UnaryConnective.NEGATION,
            logic.BinaryFormula(
                logic.PredicateExpression("weirdly_similar", [logic.Variable("x"), logic.Variable("y")]),
                logic.BinaryConnective.BIIMPLICATION,
                logic.UnaryFormula(
                    logic.UnaryConnective.NEGATION,
                    logic.BinaryFormula(logic.Variable("x"), logic.BinaryConnective.EQ, logic.Variable("y"))),
            )
        )

        formula_combination = logic.UnaryFormula(
            logic.UnaryConnective.NEGATION,
            logic.QuantifiedFormula(
                logic.Quantifier.UNIVERSAL,
                [logic.Variable("x"), logic.Variable("y")],
                logic.BinaryFormula(
                    logic.PredicateExpression("weirdly_similar", [logic.Variable("x"), logic.Variable("y")]),
                    logic.BinaryConnective.BIIMPLICATION,
                    logic.BinaryFormula(
                        logic.UnaryFormula(
                            logic.UnaryConnective.NEGATION,
                            logic.BinaryFormula(logic.Variable("x"), logic.BinaryConnective.EQ, logic.Variable("y"))),
                        logic.BinaryConnective.CONJUNCTION,
                        logic.BinaryFormula(
                            logic.BinaryFormula(
                                logic.PredicateExpression("weird", [logic.Variable("x")]),
                                logic.BinaryConnective.DISJUNCTION,
                                logic.UnaryFormula(
                                    logic.UnaryConnective.NEGATION,
                                    logic.PredicateExpression("normal", [logic.Variable("x")]))
                            ),
                            logic.BinaryConnective.IMPLICATION,
                            logic.PredicateExpression("weird", [logic.Variable("y")]),
                        )
                    )
                )
            )
        )

        for formula in [formula_eq, formula_biimp, formula_combination]:
            print("Formula:", formula)
            formula = logic_utils.convert_to_nnf(formula)
            print("Formula in NNF:", formula)
            # weak assertion, does not test correct propagation of negation
            self.assertNotIsInstance(formula, logic.UnaryFormula)

    def testCNF(self):
        formula = logic.BinaryFormula(
            logic.PredicateExpression("weirdly_similar", [logic.Variable("x"), logic.Variable("y")]),
            logic.BinaryConnective.DISJUNCTION,
            logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, [
                logic.UnaryFormula(logic.UnaryConnective.NEGATION,
                                   logic.BinaryFormula(logic.Variable("x"), logic.BinaryConnective.EQ,
                                                       logic.Variable("y"))),
                logic.BinaryFormula(
                    logic.PredicateExpression("weird", [logic.Variable("x")]),
                    logic.BinaryConnective.DISJUNCTION,
                    logic.UnaryFormula(
                        logic.UnaryConnective.NEGATION,
                        logic.PredicateExpression("normal", [logic.Variable("x")]))
                ),
                logic.PredicateExpression("weird", [logic.Variable("y")]),
            ])
        )
        print("Formula:", formula)
        formula = logic_utils.convert_to_cnf(formula)
        print("Formula in CNF:", formula)
        self.assertIsInstance(formula, logic.NaryFormula)
        self.assertEqual(formula.operator, logic.BinaryConnective.CONJUNCTION)
        for clause in formula.formulae:
            self.assertIsInstance(clause, logic.NaryFormula)
            self.assertEqual(clause.operator, logic.BinaryConnective.DISJUNCTION)
            for literal in clause.formulae:
                self.assertTrue(logic_utils.is_literal(literal))


if __name__ == '__main__':
    unittest.main()
