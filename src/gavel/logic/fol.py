from enum import Enum
from itertools import chain
from typing import Iterable

class FOLElement:
    __visit_name__ = "undefined"

    requires_parens = False

    def symbols(self) -> Iterable:
        return []


class Quantifier(Enum):

    __visit_name__ = "quantifier"

    UNIVERSAL = 0
    EXISTENTIAL = 1

    def is_universal(self):
        return self == Quantifier.UNIVERSAL

    def is_existential(self):
        return self == Quantifier.EXISTENTIAL

    def __repr__(self):
        if self.is_universal():
            return u"\u2200"
        elif self.is_existential():
            return u"\u2203"
        else:
            raise NotImplementedError


class FormulaRole(Enum):

    __visit_name__ = "formula_role"

    AXIOM = 0
    HYPOTHESIS = 1
    DEFINITION = 2
    ASSUMPTION = 3
    LEMMA = 4
    THEOREM = 5
    COROLLARY = 6
    CONJECTURE = 7
    PLAIN = 8
    FI_DOMAIN = 9
    FI_FUNCTORS = 10
    FI_PREDICATES = 11
    UNKNOWN = 12
    TYPE = 13
    NEGATED_CONJECTURE = 14

    def __repr__(self):
        return self.name


class BinaryConnective(Enum):

    __visit_name__ = "binary_connective"

    CONJUNCTION = 0
    DISJUNCTION = 1
    BIIMPLICATION = 2
    IMPLICATION = 3
    REVERSE_IMPLICATION = 4
    SIMILARITY = 5
    NEGATED_CONJUNCTION = 6
    NEGATED_DISJUNCTION = 7
    EQ = 8
    NEQ = 9
    APPLY = 10
    MAPPING = 11
    PRODUCT = 12
    UNION = 13
    GENTZEN_ARROW = 14
    ASSIGN = 15
    ARROW = 16

    def __repr__(self):
        if self == BinaryConnective.CONJUNCTION:
            return "&"
        if self == BinaryConnective.DISJUNCTION:
            return "|"
        if self == BinaryConnective.BIIMPLICATION:
            return "<=>"
        if self == BinaryConnective.IMPLICATION:
            return "=>"
        if self == BinaryConnective.REVERSE_IMPLICATION:
            return "<="
        if self == BinaryConnective.SIMILARITY:
            return "<~>"
        if self == BinaryConnective.NEGATED_CONJUNCTION:
            return "~&"
        if self == BinaryConnective.NEGATED_DISJUNCTION:
            return "~|"
        if self == BinaryConnective.EQ:
            return "="
        if self == BinaryConnective.NEQ:
            return "!="
        if self == BinaryConnective.APPLY:
            return "@"
        if self == BinaryConnective.PRODUCT:
            return "*"
        if self == BinaryConnective.UNION:
            return "+"
        if self == BinaryConnective.GENTZEN_ARROW:
            return "-->"
        if self == BinaryConnective.ASSIGN:
            return ":="
        if self == BinaryConnective.ARROW:
            return ">"


class DefinedPredicate(Enum):

    __visit_name__ = "defined_predicate"

    DISTINCT = 0
    LESS = 1
    LESS_EQ = 2
    GREATER = 3
    GREATER_EQ = 4
    IS_INT = 5
    IS_RAT = 6
    BOX_P = 7
    BOX_I = 8
    BOX_INT = 9
    BOX = 10
    DIA_P = 11
    DIA_I = 12
    DIA_INT = 13
    DIA = 14

    def __repr__(self):
        return self.name


class UnaryConnective(Enum):

    __visit_name__ = "unary_connective"

    NEGATION = 0

    def __repr__(self):
        if self == UnaryConnective.NEGATION:
            return "~"


class UnaryFormula(FOLElement):

    __visit_name__ = "unary_formula"

    def __init__(self, connective, formula: FOLElement):
        self.connective = connective
        self.formula = formula

    def __str__(self):
        return "%s(%s)" % (repr(self.connective), self.formula)

    def symbols(self):
        return self.formula.symbols()


class QuantifiedFormula(FOLElement):

    __visit_name__ = "quantified_formula"

    def __init__(self, quantifier, variables, formula):
        self.quantifier = quantifier
        self.variables = variables
        self.formula = formula

    def __str__(self):
        return "%s[%s]: %s" % (
            repr(self.quantifier),
            ", ".join(self.variables),
            self.formula,
        )

    def symbols(self):
        for symbol in self.variables:
            yield symbol.symbols()
        for symbol in self.formula.symbols():
            yield symbol


class AnnotatedFormula(FOLElement):

    __visit_name__ = "annotated_formula"

    def __init__(self, logic, name, role: FormulaRole, formula):
        self.logic = logic
        self.name = name
        self.role = role
        self.formula = formula

    def symbols(self):
        return self.formula.symbols()


class BinaryFormula(FOLElement):

    __visit_name__ = "binary_formula"

    requires_parens = True

    def __init__(self, left:FOLElement, operator, right:FOLElement):
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self):
        return "(%s) %s (%s)" % (self.left, repr(self.operator), self.right)

    def symbols(self):
        return chain(self.left.symbols(), self.right.symbols())


class FunctorExpression(FOLElement):

    __visit_name__ = "functor_expression"

    def __init__(self, functor, arguments: Iterable[FOLElement]):
        self.functor = functor
        self.arguments = arguments

    def __str__(self):
        return "%s(%s)" % (self.functor, ", ".join(map(str, self.arguments)))

    def symbols(self):
        yield self.functor
        return chain(*map(lambda x: x.symbols(), self.arguments))

class PredicateExpression(FOLElement):

    __visit_name__ = "predicate_expression"

    def __init__(self, predicate, arguments):
        self.predicate = predicate
        self.arguments = arguments

    def __str__(self):
        return "%s(%s)" % (self.predicate, ", ".join(self.arguments))

    def symbols(self):
        yield self.predicate
        return chain(*map(lambda x: x.symbols(), self.arguments))


class TypedVariable(FOLElement):

    __visit_name__ = "typed_variable"

    def __init__(self, name, vtype):
        self.name = name
        self.vtype = vtype

    def symbols(self):
        yield self.name

class TypeFormula(FOLElement):

    __visit_name__ = "type_formula"

    def __init__(self, name, type_expression):
        self.name = name
        self.type = type_expression

    def symbols(self):
        yield self.name

class Conditional(FOLElement):

    __visit_name__ = "conditional"

    def __init__(
        self,
        if_clause: FOLElement,
        then_clause: FOLElement,
        else_clause: FOLElement):

        self.if_clause = if_clause
        self.then_clause = then_clause
        self.else_clause = else_clause

    def symbols(self):
        return chain(self.if_clause.symbols(),
                     self.then_clause.symbols(),
                     self.else_clause.symbols())

class Let(FOLElement):

    __visit_name__ = "let"

    def __init__(self, types, definitions, formula):
        self.types = types
        self.definitions = definitions
        self.formula = formula

    def symbols(self):
        return self.formula.symbols()


class Subtype(FOLElement):

    __visit_name__ = "subtype"

    def __init__(self, left, right):
        self.left = left
        self.right = right


class QuantifiedType(FOLElement):

    __visit_name__ = "quantified_type"

    def __init__(self, variables, vtype):
        self.variables = variables
        self.vtype = vtype


class Import(FOLElement):

    __visit_name__ = "import"

    def __init__(self, path):
        self.path = path.replace("'", "")


class MappingType(FOLElement):

    __visit_name__ = "mapping_type"

    def __init__(self, left, right):
        self.left = left
        self.right = right


class EOFException(Exception):
    pass
