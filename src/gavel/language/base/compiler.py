import gavel.logic.fol as fol


class Compiler:
    def parenthesise(self, element: fol.FOLElement):
        if isinstance(element, str):
            return element
        result = self.visit(element)
        if element.requires_parens:
            return "(" + result + ")"
        else:
            return result

    def visit(self, obj):
        if isinstance(obj, str):
            return obj
        meth = getattr(self, "visit_%s" % obj.__visit_name__, None)

        if meth is None:
            raise Exception(
                "Compiler '{name}' not found for {cls}".format(
                    name=obj.__visit_name__,
                    cls=type(obj)
                )
            )
        return meth(obj)

    def visit_quantifier(self, quantifier: fol.Quantifier):
        if quantifier.is_universal():
            return "!"
        else:
            return "?"

    def visit_formula_role(self, role: fol.FormulaRole):
        if role == fol.FormulaRole.AXIOM:
            return "axiom"
        elif role == fol.FormulaRole.HYPOTHESIS:
            return "hypothesis"
        elif role == fol.FormulaRole.DEFINITION:
            return "definition"
        elif role == fol.FormulaRole.ASSUMPTION:
            return "assumption"
        elif role == fol.FormulaRole.LEMMA:
            return "lemma"
        elif role == fol.FormulaRole.THEOREM:
            return "theorem"
        elif role == fol.FormulaRole.COROLLARY:
            return "corollary"
        elif role == fol.FormulaRole.CONJECTURE:
            return "conjecture"
        elif role == fol.FormulaRole.PLAIN:
            return "plain"
        elif role == fol.FormulaRole.FI_DOMAIN:
            return "fi_domain"
        elif role == fol.FormulaRole.FI_FUNCTORS:
            return "fi_functors"
        elif role == fol.FormulaRole.FI_PREDICATES:
            return "fi_predicates"
        elif role == fol.FormulaRole.UNKNOWN:
            return "unknown"
        elif role == fol.FormulaRole.TYPE:
            return "type"
        elif role == fol.FormulaRole.NEGATED_CONJECTURE:
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
            self.visit(formula.connective), self.visit(formula.formula)
        )

    def visit_quantified_formula(self, formula: fol.QuantifiedFormula):
        return "{}[{}]:{}".format(
            self.visit(formula.quantifier),
            ",".join(map(self.visit, formula.variables)),
            self.parenthesise(formula.formula),
        )

    def visit_annotated_formula(self, anno: fol.AnnotatedFormula):
        return "{}({},{},({})).".format(
            anno.logic, anno.name, self.visit(anno.role), self.visit(anno.formula)
        )

    def visit_binary_formula(self, formula: fol.BinaryFormula):
        return "{}{}{}".format(
            self.parenthesise(formula.left),
            self.visit(formula.operator),
            self.parenthesise(formula.right),
        )

    def visit_functor_expression(self, expression: fol.FunctorExpression):
        return "{}({})".format(
            self.visit(expression.functor),
            ",".join(map(self.visit, expression.arguments)),
        )

    def visit_predicate_expression(self, expression: fol.PredicateExpression):
        return "{}({})".format(
            self.visit(expression.predicate),
            ",".join(map(self.visit, expression.arguments)),
        )

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

    def visit_import(self, imp: fol.Import):
        return "import(%s)" % imp.path

    def visit_mapping_type(self, expression: fol.Subtype):
        return "{}>{}".format(self.visit(expression.left), self.visit(expression.right))

    def visit_variable(self, variable: fol.Variable):
        return variable.symbol
