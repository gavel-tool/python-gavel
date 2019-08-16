import gavel.logic.fol as fol
from gavel.dialects.base.compiler import Compiler


class DBCompiler(Compiler):
    def visit_quantifier(self, quantifier: fol.Quantifier):
        raise NotImplementedError

    def visit_formula_role(self, role: fol.FormulaRole):
        raise NotImplementedError

    def visit_binary_connective(self, connective: fol.BinaryConnective):
        raise NotImplementedError

    def visit_defined_predicate(self, predicate: fol.DefinedPredicate):
        raise NotImplementedError

    def visit_unary_connective(self, predicate: fol.UnaryConnective):
        raise NotImplementedError

    def visit_unary_formula(self, formula: fol.UnaryFormula):
        raise NotImplementedError

    def visit_quantified_formula(self, formula: fol.QuantifiedFormula):
        raise NotImplementedError

    def visit_annotated_formula(self, anno: fol.AnnotatedFormula):
        raise NotImplementedError

    def visit_binary_formula(self, formula: fol.BinaryFormula):
        raise NotImplementedError

    def visit_functor_expression(self, expression: fol.FunctorExpression):
        raise NotImplementedError

    def visit_predicate_expression(self, expression: fol.PredicateExpression):
        raise NotImplementedError

    def visit_typed_variable(self, variable: fol.TypedVariable):
        raise NotImplementedError

    def visit_type_formula(self, formula: fol.TypeFormula):
        raise NotImplementedError

    def visit_conditional(self, conditional: fol.Conditional):
        raise NotImplementedError

    def visit_let(self, expression: fol.Let):
        raise NotImplementedError

    def visit_subtype(self, expression: fol.Subtype):
        raise NotImplementedError

    def visit_quantified_type(self, expression: fol.QuantifiedType):
        raise NotImplementedError

    def visit_import(self, imp: fol.Import):
        raise NotImplementedError

    def visit_mapping_type(self, expression: fol.Subtype):
        raise NotImplementedError

    def visit_variable(self, variable: fol.Variable):
        raise NotImplementedError

    def visit_constant(self, variable: fol.Variable):
        raise NotImplementedError

    def visit_problem(self, problem: fol.Problem):
        raise NotImplementedError
