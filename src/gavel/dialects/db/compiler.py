import gavel.logic.logic as fol
from gavel.dialects.base.compiler import Compiler
from gavel.logic import problem
from gavel.dialects.db.structures import Formula

class DBCompiler(Compiler):
    def visit_quantifier(self, quantifier: fol.Quantifier):
        if quantifier.is_existential():
            return dict(type="quantifier", quantifier="existential")
        elif quantifier.is_universal():
            return dict(type="quantifier", quantifier="universial")

    def visit_formula_role(self, role: problem.FormulaRole):
        if role == problem.FormulaRole.ASSUMPTION:
            return dict(type="formula_role", formula_role="assumption")
        elif role == problem.FormulaRole.AXIOM:
            return dict(type="formula_role", formula_role="axiom")
        elif role == problem.FormulaRole.CONJECTURE:
            return dict(type="formula_role", formula_role="conjecture")
        elif role == problem.FormulaRole.COROLLARY:
            return dict(type="formula_role", formula_role="corollary")
        elif role == problem.FormulaRole.DEFINITION:
            return dict(type="formula_role", formula_role="definition")
        elif role == problem.FormulaRole.FI_DOMAIN:
            return dict(type="formula_role", formula_role="fi_domain")
        elif role == problem.FormulaRole.FI_FUNCTORS:
            return dict(type="formula_role", formula_role="fi_functors")
        elif role == problem.FormulaRole.FI_PREDICATES:
            return dict(type="formula_role", formula_role="fi_predicates")
        elif role == problem.FormulaRole.HYPOTHESIS:
            return dict(type="formula_role", formula_role="hypothesis")
        elif role == problem.FormulaRole.LEMMA:
            return dict(type="formula_role", formula_role="lemma")
        elif role == problem.FormulaRole.NEGATED_CONJECTURE:
            return dict(type="formula_role", formula_role="negated_conjecture")
        elif role == problem.FormulaRole.PLAIN:
            return dict(type="formula_role", formula_role="plain")
        elif role == problem.FormulaRole.THEOREM:
            return dict(type="formula_role", formula_role="theorem")
        elif role == problem.FormulaRole.TYPE:
            return dict(type="formula_role", formula_role="type")
        elif role == problem.FormulaRole.UNKNOWN:
            return dict(type="formula_role", formula_role="unknown")
        raise NotImplementedError

    def visit_binary_connective(self, connective: fol.BinaryConnective):
        return dict(type="binary_connective", binary_connective=connective.name.lower())

    def visit_defined_predicate(self, predicate: fol.DefinedPredicate):
        return dict(type="defined_predicate", defined_predicate=predicate.name.lower())

    def visit_unary_connective(self, connective: fol.UnaryConnective):
        return dict(type="unary_connective", unary_connective=connective.name.lower())

    def visit_unary_formula(self, formula: fol.UnaryFormula):
        return dict(
            type="unary_formula",
            formula=self.visit(formula.formula),
            connective=self.visit(formula.connective),
        )

    def visit_quantified_formula(self, formula: fol.QuantifiedFormula):
        return dict(
            type="quantified_formula",
            formula=self.visit(formula.formula),
            quantifier=self.visit(formula.quantifier),
            variables=[self.visit(v) for v in formula.variables],
        )

    def visit_annotated_formula(self, anno: problem.AnnotatedFormula):
        return Formula(
            json=self.visit(anno.formula),
            name=self.visit(anno.name),
            logic=self.visit(anno.logic),
        )

    def visit_binary_formula(self, formula: fol.BinaryFormula):
        return dict(
            type="binary_formula",
            left=self.visit(formula.left),
            right=self.visit(formula.right),
            connective=self.visit(formula.operator),
        )

    def visit_functor_expression(self, expression: fol.FunctorExpression):
        return dict(
            type="functor_expression",
            arguments=[self.visit(a) for a in expression.arguments],
            functor=self.visit(expression.functor),
        )

    def visit_predicate_expression(self, expression: fol.PredicateExpression):
        return dict(
            type="predicate_expression",
            arguments=[self.visit(a) for a in expression.arguments],
            predicate=self.visit(expression.predicate),
        )

    def visit_conditional(self, conditional: fol.Conditional):
        return dict(
            type="conditional",
            if_clause=conditional.if_clause,
            then_clause=conditional.then_clause,
            else_clause=conditional.else_clause,
        )

    def visit_import(self, imp: fol.Import):
        return dict(type="import", path=imp.path)

    def visit_variable(self, variable: fol.Variable):
        return dict(type="variable", symbol=variable.symbol)

    def visit_constant(self, variable: fol.Variable):
        return dict(type="constant", symbol=variable.symbol)

    def visit_problem(self, problem: problem.Problem):
        return dict(
            type="problem",
            premises=[self.visit(p) for p in problem.premises],
            conjecture=self.visit(problem.conjecture),
        )
