import gavel.logic.logic as fol
from gavel.dialects.base.compiler import Compiler
from gavel.logic import problem
import re


class TPTPCompiler(Compiler):

    def __init__(self, shorten_names=False, keep_annotations=True):
        self.shorten_names = shorten_names
        self.keep_annotations = keep_annotations
        # maps symbols used in internal Gavel to symbols in TPTP output
        self.name_mapping = {}

    def visit_defined_constant(self, obj: fol.DefinedConstant):
        return self.visit(obj.value)

    def parenthesise(self, element: fol.LogicElement):
        if isinstance(element, str):
            return element
        result = self.visit(element)
        if hasattr(element, "requires_parens") and element.requires_parens:
            return "(" + result + ")"
        else:
            return result

    def visit(self, obj, **kwargs):
        if isinstance(obj, str):
            return obj
        meth = getattr(self, "visit_%s" % obj.__visit_name__, None)

        if meth is None:
            raise Exception(
                "Compiler '{name}' not found for {cls}".format(
                    name=obj.__visit_name__, cls=type(obj)
                )
            )
        return meth(obj, **kwargs)

    def visit_quantifier(self, quantifier: fol.Quantifier):
        if quantifier.is_universal():
            return "!"
        else:
            return "?"

    def visit_formula_role(self, role: problem.FormulaRole):
        if role == problem.FormulaRole.AXIOM:
            return "axiom"
        elif role == problem.FormulaRole.HYPOTHESIS:
            return "hypothesis"
        elif role == problem.FormulaRole.DEFINITION:
            return "definition"
        elif role == problem.FormulaRole.ASSUMPTION:
            return "assumption"
        elif role == problem.FormulaRole.LEMMA:
            return "lemma"
        elif role == problem.FormulaRole.THEOREM:
            return "theorem"
        elif role == problem.FormulaRole.COROLLARY:
            return "corollary"
        elif role == problem.FormulaRole.CONJECTURE:
            return "conjecture"
        elif role == problem.FormulaRole.PLAIN:
            return "plain"
        elif role == problem.FormulaRole.FINITE_INTERPRETATION_DOMAIN:
            return "fi_domain"
        elif role == problem.FormulaRole.FINITE_INTERPRETATION_FUNCTORS:
            return "fi_functors"
        elif role == problem.FormulaRole.FINITE_INTERPRETATION_PREDICATES:
            return "fi_predicates"
        elif role == problem.FormulaRole.UNKNOWN:
            return "unknown"
        elif role == problem.FormulaRole.TYPE:
            return "type"
        elif role == problem.FormulaRole.NEGATED_CONJECTURE:
            return "negated_conjecture"
        else:
            raise NotImplementedError

    def visit_binary_connective(self, connective: fol.BinaryConnective):
        if connective == fol.BinaryConnective.CONJUNCTION:
            return "&"
        elif connective == fol.BinaryConnective.DISJUNCTION:
            return "|"
        elif connective == fol.BinaryConnective.BIIMPLICATION:
            return "<=>"
        elif connective == fol.BinaryConnective.IMPLICATION:
            return "=>"
        elif connective == fol.BinaryConnective.REVERSE_IMPLICATION:
            return "<="
        elif connective == fol.BinaryConnective.SIMILARITY:
            return "<~>"
        elif connective == fol.BinaryConnective.NEGATED_CONJUNCTION:
            return "!&"
        elif connective == fol.BinaryConnective.NEGATED_DISJUNCTION:
            return "!|"
        elif connective == fol.BinaryConnective.EQ:
            return "="
        elif connective == fol.BinaryConnective.NEQ:
            return "!="
        elif connective == fol.BinaryConnective.APPLY:
            return "@"
        elif connective == fol.BinaryConnective.MAPPING:
            return ":"
        elif connective == fol.BinaryConnective.PRODUCT:
            return "*"
        elif connective == fol.BinaryConnective.UNION:
            return "U"
        elif connective == fol.BinaryConnective.GENTZEN_ARROW:
            return "-->"
        elif connective == fol.BinaryConnective.ASSIGN:
            return ":="
        elif connective == fol.BinaryConnective.ARROW:
            return ">"
        else:
            raise NotImplementedError

    def visit_defined_predicate(self, predicate: fol.DefinedPredicate):
        if predicate == fol.DefinedPredicate.DISTINCT:
            return "$distinct"
        elif predicate == fol.DefinedPredicate.LESS:
            return "$less"
        elif predicate == fol.DefinedPredicate.LESS_EQ:
            return "$lesseq"
        elif predicate == fol.DefinedPredicate.GREATER:
            return "$greater"
        elif predicate == fol.DefinedPredicate.GREATER_EQ:
            return "$greatereq"
        elif predicate == fol.DefinedPredicate.IS_INT:
            return "$is_int"
        elif predicate == fol.DefinedPredicate.IS_RAT:
            return "$is_rat"
        elif predicate == fol.DefinedPredicate.BOX_P:
            return "$box_P"
        elif predicate == fol.DefinedPredicate.BOX_I:
            return "$box_i"
        elif predicate == fol.DefinedPredicate.BOX_INT:
            return "$box_int"
        elif predicate == fol.DefinedPredicate.BOX:
            return "$box"
        elif predicate == fol.DefinedPredicate.DIA_P:
            return "$dia_P"
        elif predicate == fol.DefinedPredicate.DIA_I:
            return "$dia_i"
        elif predicate == fol.DefinedPredicate.DIA_INT:
            return "$dia_int"
        elif predicate == fol.DefinedPredicate.DIA:
            return "$dia"
        else:
            raise NotImplementedError

    def visit_unary_connective(self, predicate: fol.UnaryConnective):
        if predicate == fol.UnaryConnective.NEGATION:
            return "~"
        else:
            raise NotImplementedError

    def visit_unary_formula(self, formula: fol.UnaryFormula):
        return "{}{}".format(
            self.visit(formula.connective), self.parenthesise(formula.formula)
        )

    def visit_quantified_formula(self, formula: fol.QuantifiedFormula):
        return "{}[{}]:{}".format(
            self.visit(formula.quantifier),
            ",".join(map(self.visit, formula.variables)),
            self.parenthesise(formula.formula),
        )

    def visit_annotated_formula(self, anno: problem.AnnotatedFormula):
        if anno.annotation is None or not self.keep_annotations:
            return "{}({},{},({})).".format(
                anno.logic, anno.name, self.visit(anno.role), self.visit(anno.formula)
            )
        return "% {}\n{}({},{},({})).".format(
            anno.annotation.replace("\n", "\n% "), anno.logic, anno.name, self.visit(anno.role), self.visit(anno.formula)
        )

    def visit_binary_formula(self, formula: fol.BinaryFormula, parent_operand=None):
        if formula.operator.is_associative and isinstance(
            formula.left, fol.BinaryFormula
        ):
            lhr = self.visit(formula.left, parent_operand=formula.operator)
        else:
            lhr = self.parenthesise(formula.left)

        if formula.operator.is_associative and isinstance(
            formula.right, fol.BinaryFormula
        ):
            rhr = self.visit(formula.right, parent_operand=formula.operator)
        else:
            rhr = self.parenthesise(formula.right)

        s = "{}{}{}".format(lhr, self.visit(formula.operator), rhr)
        if parent_operand is None or parent_operand == formula.operator:
            return s
        else:
            return "(" + s + ")"

    def visit_functor_expression(self, expression: fol.FunctorExpression):
        name = ""
        if expression.functor:
            name = self.shorten_name(expression.functor)
            name = name[:1].lower() + name[1:]
            name = re.sub("[^A-z_0-9]", "_", name)
            self.name_mapping[expression.functor] = name
        return "'{}'({})".format(name, ",".join(map(self.visit, expression.arguments)))

    def visit_predicate_expression(self, expression: fol.PredicateExpression):
        name = ""
        if expression.predicate:
            name = self.shorten_name(expression.predicate)
            name = name[:1].lower() + name[1:]
            name = re.sub("[^A-z_0-9]", "_", name)
            self.name_mapping[expression.predicate] = name
        return "'{}'({})".format(name, ",".join(map(self.visit, expression.arguments)))

    def visit_typed_variable(self, variable: fol.TypedVariable):
        return "{}:{}".format(variable.name, self.visit(variable.vtype))

    def visit_type_formula(self, formula: fol.TypeFormula):
        return "({}):{}".format(self.visit(formula.name), self.visit(formula.type))

    def visit_conditional(self, conditional: fol.Conditional):
        return "if ({}) then ({}) else ({})".format(
            self.visit(conditional.if_clause),
            self.visit(conditional.then_clause),
            self.visit(conditional.else_clause),
        )

    def visit_let(self, expression: fol.Let):
        return "let ({}) with ({}) in ({})".format(
            self.visit(expression.types),
            self.visit(expression.definitions),
            self.visit(expression.formula),
        )

    def visit_subtype(self, expression: fol.Subtype):
        return "{} <= {})".format(
            self.visit(expression.left), self.visit(expression.right)
        )

    def visit_quantified_type(self, expression: fol.QuantifiedType):
        return ">![{}]:{}".format(
            self.visit(fol.Quantifier.EXISTENTIAL),
            self.visit(expression.variables),
            self.visit(expression.vtype),
        )

    def visit_mapping_type(self, expression: fol.Subtype):
        return "{}>{}".format(self.visit(expression.left), self.visit(expression.right))

    def visit_variable(self, variable: fol.Variable):
        name = ""
        if variable.symbol:
            name = self.shorten_name(variable.symbol)
            name = name[:1].upper() + name[1:]
            name = re.sub("[^A-z_0-9]", "_", name)
            self.name_mapping[variable.symbol] = name
        return name

    def visit_distinct_object(self, variable: fol.DistinctObject):
        return "\"" + variable.symbol + "\""

    def visit_constant(self, constant: fol.Constant):
        name = ""
        if constant.symbol:
            name = self.shorten_name(constant.symbol)
            name = name[:1].lower() + name[1:]
            name = re.sub('[^A-z_0-9]', '_', name)
            self.name_mapping[constant.symbol] = name
        return f"'{name}'"

    def visit_problem(self, problem: problem.Problem):
        L = [self.visit(i) for i in problem.imports] + [self.visit(axiom) for axiom in problem.premises] + [self.visit(c) for c in problem.conjectures]
        return "\n".join(L)

    def visit_predefined_constant(self, obj: fol.PredefinedConstant):
        if obj == fol.PredefinedConstant.FALSUM:
            return "$false"
        elif obj == fol.PredefinedConstant.VERUM:
            return "$true"
        else:
            raise NotImplementedError

    def visit_import(self, imp: problem.Import):
        return "import(%s)" % imp.path

    def shorten_name(self, name):
        cut_position = 0
        # shorten name by taking only part after last / or # (but at least 3 characters)
        # e.g. http://example.org/part_of -> part_of
        if self.shorten_names and len(name) > 2:
            slash_pos = name[:-3].rfind("/")
            hashtag_pos = name[:-3].rfind("#")
            if slash_pos > 0:
                cut_position = slash_pos + 1
            if hashtag_pos > slash_pos:
                cut_position = hashtag_pos + 1

        return name[cut_position:]
