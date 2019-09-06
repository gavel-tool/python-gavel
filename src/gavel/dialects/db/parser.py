from gavel.dialects.base.parser import LogicParser
from gavel.dialects.base.parser import Parseable
from gavel.dialects.base.parser import ProblemParser
from gavel.logic import fol
from gavel.logic.base import Problem
from gavel.logic.base import Sentence


class DBProblemParser(ProblemParser):
    logic_parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        self.logic_parser = LogicParser(*args, **kwargs)

    def parse(self, structure: Parseable, *args, **kwargs):
        premises = []
        conjectures = []
        for s in self.logic_parser.parse(structure):
            if isinstance(s, Sentence):
                if s.is_conjecture():
                    conjectures.append(s)
                else:
                    premises.append(s)
        for c in conjectures:
            yield Problem(premises, c)


class DBFOLParser(LogicParser):
    def _parse_rec(self, obj, *args, **kwargs):
        if isinstance(obj, str):
            return obj
        meth = getattr(self, "parse_%s" % obj.get("type"), None)

        if meth is None:
            raise Exception(
                "Parser '{name}' not found for {cls}".format(
                    name=obj.get("type"), cls=obj
                )
            )
        return meth(obj)

    def parse_quantifier(self, quantifier: dict):
        if quantifier.get("type") == "existential":
            q = fol.Quantifier.EXISTENTIAL
        elif quantifier.get("type") == "universial":
            q = fol.Quantifier.UNIVERSAL
        else:
            raise NotImplementedError
        return dict(type="quantifier", quantifier=q)

    def parse_formula_role(self, role: dict):
        return getattr(fol.FormulaRole, role["formula_role"].upper())

    def parse_binary_connective(self, connective: dict):
        return getattr(fol.BinaryConnective, connective["binary_connective"].upper())

    def parse_defined_predicate(self, predicate: dict):
        return getattr(fol.DefinedPredicate, predicate["defined_predicate"].upper())

    def parse_unary_connective(self, connective: dict):
        return getattr(fol.UnaryConnective, connective["unary_connective"].upper())

    def parse_unary_formula(self, formula: dict):
        return fol.UnaryFormula(
            formula=self._parse_rec(formula["formula"]),
            connective=self._parse_rec(formula["connective"]),
        )

    def parse_quantified_formula(self, formula: dict):
        return fol.QuantifiedFormula(
            formula=self._parse_rec(formula["formula"]),
            quantifier=self._parse_rec(formula["quantifier"]),
            variables=[self._parse_rec(v) for v in formula["quantifier"]],
        )

    def parse_annotated_formula(self, anno: dict):
        return fol.AnnotatedFormula(
            formula=self._parse_rec(anno["formula"]),
            name=anno["name"],
            role=self._parse_rec(anno["role"]),
            logic=anno["logic"],
        )

    def parse_binary_formula(self, formula: dict):
        return fol.BinaryFormula(
            left=self._parse_rec(formula["left"]),
            right=self._parse_rec(formula["right"]),
            operator=self._parse_rec(formula["connective"]),
        )

    def parse_functor_expression(self, expression: fol.FunctorExpression):
        return fol.FunctorExpression(
            functor=self._parse_rec(expression["functor"]),
            arguments=[self._parse_rec(a) for a in expression["arguments"]],
        )

    def parse_predicate_expression(self, expression: dict) -> fol.PredicateExpression:
        return fol.PredicateExpression(
            predicate=self._parse_rec(expression["functor"]),
            arguments=[self._parse_rec(a) for a in expression["arguments"]],
        )

    def parse_conditional(self, conditional: dict) -> fol.Conditional:
        return fol.Conditional(
            if_clause=self._parse_rec(conditional["if_clause"]),
            then_clause=self._parse_rec(conditional["then_clause"]),
            else_clause=self._parse_rec(conditional["else_clause"]),
        )

    def parse_import(self, imp: dict) -> fol.Import:
        return fol.Import(path=imp["path"])

    def parse_variable(self, variable: dict) -> fol.Variable:
        return fol.Variable(symbol=variable["symbol"])

    def parse_constant(self, variable: dict):
        return fol.Constant(symbol=variable["symbol"])

    def parse_problem(self, problem: dict) -> fol.Problem:
        return fol.Problem(
            premises=[self._parse_rec(p) for p in problem["premises"]],
            conjecture=self._parse_rec(problem["conjecture"]),
        )
