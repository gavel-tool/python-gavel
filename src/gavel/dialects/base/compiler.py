import gavel.logic.logic as fol
from gavel.logic import problem


class Compiler:
    def visit(self, obj, *args, **kwargs):
        if isinstance(obj, str):
            return obj
        if hasattr(obj, "__visit_name__"):
            meth = getattr(self, "visit_%s" % obj.__visit_name__, None)
        else:
            raise Exception(f"{obj} has no visitor name")
        if meth is None:
            raise Exception(
                "Compiler '{name}' not found for {cls}".format(
                    name=obj.__visit_name__, cls=type(obj)
                )
            )
        return meth(obj, **kwargs)

    def visit_quantifier(self, quantifier: fol.Quantifier):
        raise NotImplementedError

    def visit_formula_role(self, role: problem.FormulaRole):
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

    def visit_annotated_formula(self, anno: problem.AnnotatedFormula):
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

    def visit_mapping_type(self, expression: fol.Subtype):
        raise NotImplementedError

    def visit_variable(self, variable: fol.Variable):
        raise NotImplementedError

    def visit_constant(self, variable: fol.Variable):
        raise NotImplementedError

    def visit_problem(self, problem: problem.Problem):
        raise NotImplementedError

    def visit_type(self, problem: fol.Type):
        raise NotImplementedError

    def visit_distinct_object(self, obj: fol.DistinctObject):
        raise NotImplementedError

    def visit_defined_constant(self, obj: fol.DefinedConstant):
        raise NotImplementedError

    def visit_predefined_constant(self, obj: fol.PredefinedConstant):
        raise NotImplementedError
