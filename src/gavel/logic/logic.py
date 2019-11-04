from enum import Enum
from itertools import chain
from typing import Iterable


class LogicElement:
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
            return "\u2200"
        elif self.is_existential():
            return "\u2203"
        else:
            raise NotImplementedError


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
    PRODUCT = 12
    UNION = 13
    GENTZEN_ARROW = 14
    ASSIGN = 15
    ARROW = 16

    def is_associative(self):
        return self in (
            BinaryConnective.DISJUNCTION,
            BinaryConnective.CONJUNCTION,
            BinaryConnective.EQ,
        )

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
        else:
            raise Exception(self)


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


class UnaryFormula(LogicElement):
    """
    Attributes
    ----------

    connective:
        A unary connective
    formula:
        A formula

    """

    __visit_name__ = "unary_formula"

    def __init__(self, connective, formula: LogicElement):
        self.connective = connective
        self.formula = formula

    def __str__(self):
        return "%s(%s)" % (repr(self.connective), self.formula)

    def symbols(self):
        return self.formula.symbols()


class QuantifiedFormula(LogicElement):
    """
    Attributes
    ----------

    quantifier:
        A quantier (existential or universal)
    variables:
        A list of variables bound by the quantifier
    formula
        A logical formula
    """

    __visit_name__ = "quantified_formula"

    def __init__(self, quantifier, variables, formula):
        self.quantifier = quantifier
        self.variables = variables
        self.formula = formula

    def __str__(self):
        return "%s[%s]: %s" % (
            repr(self.quantifier),
            ", ".join(map(str, self.variables)),
            self.formula,
        )

    def symbols(self):
        variables = {
            symbol for variable in self.variables for symbol in variable.symbols()
        }
        return set(self.formula.symbols()).difference(variables)


class BinaryFormula(LogicElement):

    """
    Attributes
    ----------
    oparator
        A binary operator
    left
        The formula on the left side
    right
        The formula on the right side

    """
    __visit_name__ = "binary_formula"

    requires_parens = True

    def __init__(self, left: LogicElement, operator, right: LogicElement):
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self):
        return "(%s) %s (%s)" % (str(self.left), repr(self.operator), str(self.right))

    def symbols(self):
        return chain(self.left.symbols(), self.right.symbols())


class FunctorExpression(LogicElement):

    __visit_name__ = "functor_expression"

    def __init__(self, functor, arguments: Iterable[LogicElement]):
        self.functor = functor
        self.arguments = arguments

    def __str__(self):
        return "%s(%s)" % (self.functor, ", ".join(map(str, self.arguments)))

    def symbols(self):
        yield self.functor
        for argument in self.arguments:
            if isinstance(argument, LogicElement):
                for s in argument.symbols():
                    yield s
            elif isinstance(argument, str):
                yield argument
            else:
                raise NotImplementedError


class PredicateExpression(LogicElement):

    __visit_name__ = "predicate_expression"

    def __init__(self, predicate, arguments):
        self.predicate = predicate
        self.arguments = arguments

    def __str__(self):
        return "%s(%s)" % (self.predicate, ", ".join(map(str, self.arguments)))

    def symbols(self):
        yield self.predicate
        return chain(*map(lambda x: x.symbols(), self.arguments))


class TypedVariable(LogicElement):

    __visit_name__ = "typed_variable"

    def __init__(self, name, vtype):
        self.name = name
        self.vtype = vtype

    def symbols(self):
        yield self.name


class TypeFormula(LogicElement):

    __visit_name__ = "type_formula"

    def __init__(self, name, type_expression):
        self.name = name
        self.type = type_expression

    def symbols(self):
        yield self.name


class Conditional(LogicElement):

    __visit_name__ = "conditional"

    def __init__(
        self,
        if_clause: LogicElement,
        then_clause: LogicElement,
        else_clause: LogicElement,
    ):

        self.if_clause = if_clause
        self.then_clause = then_clause
        self.else_clause = else_clause

    def symbols(self):
        return chain(
            self.if_clause.symbols(),
            self.then_clause.symbols(),
            self.else_clause.symbols(),
        )


class Variable(LogicElement):

    __visit_name__ = "variable"

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def symbols(self):
        return set()


class Constant(LogicElement):

    __visit_name__ = "constant"

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def symbols(self):
        return {self.symbol}


class DistinctObject(LogicElement):

    __visit_name__ = "distinct_object"

    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def symbols(self):
        return {self.symbol}


class DefinedConstant(Enum):

    __visit_name__ = "defined_constant"

    VERUM = 0
    FALSUM = 1

    def __str__(self):
        if self == DefinedConstant.VERUM:
            return "$true"
        elif self == DefinedConstant.FALSUM:
            return "$false"


class Let(LogicElement):

    __visit_name__ = "let"

    def __init__(self, types, definitions, formula):
        self.types = types
        self.definitions = definitions
        self.formula = formula

    def symbols(self):
        return self.formula.symbols()


class Subtype(LogicElement):

    __visit_name__ = "subtype"

    def __init__(self, left, right):
        self.left = left
        self.right = right


class Type(LogicElement):
    __visit_name__ = "type"

    def __init__(self, name):
        self.name = name


class QuantifiedType(LogicElement):

    __visit_name__ = "quantified_type"

    def __init__(self, variables, vtype):
        self.variables = variables
        self.vtype = vtype


class Import(LogicElement):

    __visit_name__ = "import"

    def __init__(self, path):
        self.path = path.replace("'", "")


class MappingType(LogicElement):

    __visit_name__ = "mapping_type"

    def __init__(self, left, right):
        self.left = left
        self.right = right
