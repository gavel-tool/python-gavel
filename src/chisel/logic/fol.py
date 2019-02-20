from enum import Enum


class FOLElement:
    pass


class Quantifier(Enum):
    UNIVERSAL = 0
    EXISTENTIAL = 1

    def __repr__(self):
        if self == Quantifier.UNIVERSAL:
            return u"\u2200"
        elif self == Quantifier.EXISTENTIAL:
            return u"\u2203"

class FormulaRole(Enum):
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
            return '&'
        if self == BinaryConnective.DISJUNCTION:
            return '|'
        if self == BinaryConnective.BIIMPLICATION:
            return '<=>'
        if self == BinaryConnective.IMPLICATION:
            return '=>'
        if self == BinaryConnective.REVERSE_IMPLICATION:
            return '<='
        if self == BinaryConnective.SIMILARITY:
            return '<~>'
        if self == BinaryConnective.NEGATED_CONJUNCTION:
            return '~&'
        if self == BinaryConnective.NEGATED_DISJUNCTION:
            return '~|'
        if self == BinaryConnective.EQ:
            return '='
        if self == BinaryConnective.NEQ:
            return '!='
        if self == BinaryConnective.APPLY:
            return '@'
        if self == BinaryConnective.MAPPING:
            return '>'
        if self == BinaryConnective.PRODUCT:
            return '*'
        if self == BinaryConnective.UNION:
            return '+'
        if self == BinaryConnective.GENTZEN_ARROW:
            return '-->'
        if self == BinaryConnective.ASSIGN:
            return ':='
        if self == BinaryConnective.ARROW:
            return '>'

class DefinedPredicate(Enum):
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
    NEGATION = 0
    def __repr__(self):
        if self == UnaryConnective.NEGATION:
            return '~'


class UnaryFormula(FOLElement):
    def __init__(self, connective, formula):
        self.connective = connective
        self.formula = formula

    def __str__(self):
        return '%s(%s)'%(
            repr(self.connective),
            self.formula)


class QuantifiedFormula(FOLElement):
    def __init__(self, quantifier, variables, formula):
        self.quantifier = quantifier
        self.variables = variables
        self.formula = formula

    def __str__(self):
        return '%s[%s]: %s'%(
            repr(self.quantifier),
            ', '.join(self.variables),
            self.formula)


class AnnotatedFormula(FOLElement):
    def __init__(self, name, role: FormulaRole, formula):
        self.name = name
        self.role = role
        self.formula = formula

    def __str__(self):
        return '%s_%s: %s'%(
            repr(self.role),
            self.name,
            self.formula)


class BinaryFormula(FOLElement):
    def __init__(self, left, operator, right):
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self):
        return '(%s) %s (%s)'%(
            self.left,
            repr(self.operator),
            self.right)

class FunctorExpression(FOLElement):
    def __init__(self, functor, arguments):
        self.functor = functor
        self.arguments = arguments

    def __str__(self):
        return '%s(%s)'%(
            self.functor,
            ', '.join(map(str, self.arguments)))



class PredicateExpression(FOLElement):
    def __init__(self, predicate, arguments):
        self.predicate = predicate
        self.arguments = arguments

    def __str__(self):
        return '%s(%s)'%(
            self.predicate,
            ', '.join(self.arguments))


class TypedVariable(FOLElement):
    def __init__(self, name, vtype):
        self.name = name
        self.vtype = vtype


class Conditional(FOLElement):
    def __init__(self, if_clause, then_clause, else_clause):
        self.if_clause = if_clause
        self.then_clause = then_clause
        self.else_clause = else_clause

class Let(FOLElement):
    def __init__(self, types, definitions, formula):
        self.types = types
        self.definitions = definitions
        self.formula = formula

class Subtype(FOLElement):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class QuantifiedType(FOLElement):
    def __init__(self, variables, vtype):
        self.variables = variables
        self.vtype = vtype

class Import(FOLElement):
    def __init__(self, path):
        self.path=path.replace('\'', '')

class EOFException(Exception):
    pass
