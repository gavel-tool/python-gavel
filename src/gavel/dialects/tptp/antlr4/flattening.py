# Generated from tptp_v7_0_0_0.g4 by ANTLR 4.5.1
import gavel.dialects.tptp.sources as sources
from gavel.dialects.tptp.antlr4.tptp_v7_0_0_0Parser import tptp_v7_0_0_0Parser
from gavel.dialects.tptp.antlr4.tptp_v7_0_0_0Visitor import tptp_v7_0_0_0Visitor
from gavel.logic import logic
from gavel.logic import problem

# This class defines a complete generic visitor for a parse tree produced by tptp_v7_0_0_0Parser.


class FOFFlatteningVisitor(tptp_v7_0_0_0Visitor):
    def defaultResult(self):
        return None

    def aggregateResult(self, aggregate, nextResult):
        if aggregate is None:
            aggregate = []
        aggregate.append(nextResult)
        return aggregate

    def visitTerminal(self, node):
        return node.symbol.text

    def visit_first(self, ctx):
        assert len(ctx.children) == 1
        return self.visit(ctx.children[0])

    def visit_list(self, ctx):
        if len(ctx.children) == 1:
            return [self.visit(ctx.children[0])]
        else:
            return [
                self.visit(ctx.children[i * 2])
                for i in range(len(ctx.children) // 2 + 1)
            ]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tptp_file.
    def visitTptp_file(self, ctx: tptp_v7_0_0_0Parser.Tptp_fileContext):
        return [self.visit(c) for c in ctx.children[:-1]]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tptp_input.
    def visitTptp_input(self, ctx: tptp_v7_0_0_0Parser.Tptp_inputContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#annotated_formula.
    def visitAnnotated_formula(
        self, ctx: tptp_v7_0_0_0Parser.Annotated_formulaContext
    ) -> problem.AnnotatedFormula:
        annotated = ctx.children[0]
        return problem.AnnotatedFormula(
            self.visit(annotated.children[0]).replace("(", ""),
            self.visit(annotated.children[1]),  # name
            self.visit(annotated.children[3]),  # role
            self.visit(annotated.children[5]),
            annotation=self.visit(annotated.children[6])
            if len(annotated.children) > 7
            else None,
        )  # formula

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tpi_formula.
    def visitTpi_formula(self, ctx: tptp_v7_0_0_0Parser.Tpi_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#annotations.
    def visitAnnotations(self, ctx: tptp_v7_0_0_0Parser.AnnotationsContext):
        return self.visit(ctx.children[1])

    _ROLE_MAP = {
        "axiom": problem.FormulaRole.AXIOM,
        "hypothesis": problem.FormulaRole.HYPOTHESIS,
        "definition": problem.FormulaRole.DEFINITION,
        "assumption": problem.FormulaRole.ASSUMPTION,
        "lemma": problem.FormulaRole.LEMMA,
        "theorem": problem.FormulaRole.THEOREM,
        "corollary": problem.FormulaRole.COROLLARY,
        "conjecture": problem.FormulaRole.CONJECTURE,
        "negated_conjecture": problem.FormulaRole.NEGATED_CONJECTURE,
        "plain": problem.FormulaRole.PLAIN,
        "type": problem.FormulaRole.TYPE,
        "fi_domain": problem.FormulaRole.FINITE_INTERPRETATION_DOMAIN,
        "fi_functors": problem.FormulaRole.FINITE_INTERPRETATION_FUNCTORS,
        "fi_predicates": problem.FormulaRole.FINITE_INTERPRETATION_PREDICATES,
        "unknown": problem.FormulaRole.UNKNOWN,
    }

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#formula_role.
    def visitFormula_role(self, ctx: tptp_v7_0_0_0Parser.Formula_roleContext):
        return self._ROLE_MAP[self.visit_first(ctx)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_formula.
    def visitThf_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_logic_formula.
    def visitThf_logic_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_logic_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_binary_formula.
    def visitThf_binary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Thf_binary_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_binary_pair.
    def visitThf_binary_pair(self, ctx: tptp_v7_0_0_0Parser.Thf_binary_pairContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            self.visit(ctx.children[1]),
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_binary_tuple.
    def visitThf_binary_tuple(self, ctx: tptp_v7_0_0_0Parser.Thf_binary_tupleContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_or_formula.
    def visitThf_or_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_or_formulaContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.DISJUNCTION,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_and_formula.
    def visitThf_and_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_and_formulaContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.CONJUNCTION,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_apply_formula.
    def visitThf_apply_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_apply_formulaContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.APPLY,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_unitary_formula.
    def visitThf_unitary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Thf_unitary_formulaContext
    ):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        if len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_quantified_formula.
    def visitThf_quantified_formula(
        self, ctx: tptp_v7_0_0_0Parser.Thf_quantified_formulaContext
    ):
        return logic.QuantifiedFormula(
            *self.visit(ctx.children[0]), self.visit(ctx.children[1])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_quantification.
    def visitThf_quantification(
        self, ctx: tptp_v7_0_0_0Parser.Thf_quantificationContext
    ):
        return self.visit(ctx.children[0]), self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_variable_list.
    def visitThf_variable_list(self, ctx: tptp_v7_0_0_0Parser.Thf_variable_listContext):
        if len(ctx.children) == 1:
            return [self.visit_first(ctx)]
        if len(ctx.children) == 3:
            return self.visit(ctx.children[2]).append(ctx.children[0])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_variable.
    def visitThf_variable(self, ctx: tptp_v7_0_0_0Parser.Thf_variableContext):
        return self.visitVariable(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_typed_variable.
    def visitThf_typed_variable(
        self, ctx: tptp_v7_0_0_0Parser.Thf_typed_variableContext
    ):
        return logic.TypedVariable(
            self.visit(ctx.children[0]), self.visit(ctx.children[2])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_unary_formula.
    def visitThf_unary_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_unary_formulaContext):
        return logic.UnaryFormula(
            self.visit(ctx.children[0]), self.visit(ctx.children[2])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_atom.
    def visitThf_atom(self, ctx: tptp_v7_0_0_0Parser.Thf_atomContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_function.
    def visitThf_function(self, ctx: tptp_v7_0_0_0Parser.Thf_functionContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_conn_term.
    def visitThf_conn_term(self, ctx: tptp_v7_0_0_0Parser.Thf_conn_termContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_conditional.
    def visitThf_conditional(self, ctx: tptp_v7_0_0_0Parser.Thf_conditionalContext):
        return logic.Conditional(
            self.visit(ctx.children[1]),
            self.visit(ctx.children[3]),
            self.visit(ctx.children[5]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_let.
    def visitThf_let(self, ctx: tptp_v7_0_0_0Parser.Thf_letContext):
        return logic.Let(
            self.visit(ctx.children[1]),
            self.visit(ctx.children[3]),
            self.visit(ctx.children[5]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_arguments.
    def visitThf_arguments(self, ctx: tptp_v7_0_0_0Parser.Thf_argumentsContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_type_formula.
    def visitThf_type_formula(self, ctx: tptp_v7_0_0_0Parser.Thf_type_formulaContext):
        return logic.TypeFormula(
            self.visit(ctx.children[0]), self.visit(ctx.children[2])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_typeable_formula.
    def visitThf_typeable_formula(
        self, ctx: tptp_v7_0_0_0Parser.Thf_typeable_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_subtype.
    def visitThf_subtype(self, ctx: tptp_v7_0_0_0Parser.Thf_subtypeContext):
        return logic.Subtype(self.visit(ctx.children[0]), self.visit(ctx.children[2]))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_top_level_type.
    def visitThf_top_level_type(
        self, ctx: tptp_v7_0_0_0Parser.Thf_top_level_typeContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_unitary_type.
    def visitThf_unitary_type(self, ctx: tptp_v7_0_0_0Parser.Thf_unitary_typeContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_apply_type.
    def visitThf_apply_type(self, ctx: tptp_v7_0_0_0Parser.Thf_apply_typeContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_binary_type.
    def visitThf_binary_type(self, ctx: tptp_v7_0_0_0Parser.Thf_binary_typeContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_mapping_type.
    def visitThf_mapping_type(self, ctx: tptp_v7_0_0_0Parser.Thf_mapping_typeContext):
        return logic.MappingType(
            self.visit(ctx.children[0]), self.visit(ctx.children[2])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_xprod_type.
    def visitThf_xprod_type(self, ctx: tptp_v7_0_0_0Parser.Thf_xprod_typeContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.PRODUCT,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_union_type.
    def visitThf_union_type(self, ctx: tptp_v7_0_0_0Parser.Thf_union_typeContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.UNION,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_sequent.
    def visitThf_sequent(self, ctx: tptp_v7_0_0_0Parser.Thf_sequentContext):
        if isinstance(ctx.children[0], tptp_v7_0_0_0Parser.Thf_tupleContext):
            return logic.BinaryFormula(
                self.visit(ctx.children[0]),
                logic.BinaryConnective.GENTZEN_ARROW,
                self.visit(ctx.children[2]),
            )
        else:
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_tuple.
    def visitThf_tuple(self, ctx: tptp_v7_0_0_0Parser.Thf_tupleContext):
        if len(ctx.children) == 1:
            return []
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_formula_list.
    def visitThf_formula_list(self, ctx: tptp_v7_0_0_0Parser.Thf_formula_listContext):
        if len(ctx.children) == 1:
            return [self.visit_first(ctx)]
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[2]).append(self.visit(ctx.children[0]))
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tfx_formula.
    def visitTfx_formula(self, ctx: tptp_v7_0_0_0Parser.Tfx_formulaContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tfx_logic_formula.
    def visitTfx_logic_formula(self, ctx: tptp_v7_0_0_0Parser.Tfx_logic_formulaContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_formula.
    def visitTff_formula(self, ctx: tptp_v7_0_0_0Parser.Tff_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_logic_formula.
    def visitTff_logic_formula(self, ctx: tptp_v7_0_0_0Parser.Tff_logic_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_binary_formula.
    def visitTff_binary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Tff_binary_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_binary_nonassoc.
    def visitTff_binary_nonassoc(
        self, ctx: tptp_v7_0_0_0Parser.Tff_binary_nonassocContext
    ):
        return self.visitFof_binary_nonassoc(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_binary_assoc.
    def visitTff_binary_assoc(self, ctx: tptp_v7_0_0_0Parser.Tff_binary_assocContext):
        return self.visitFof_binary_assoc(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_or_formula.
    def visitTff_or_formula(self, ctx: tptp_v7_0_0_0Parser.Tff_or_formulaContext):
        return self.visitFof_or_formula(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_and_formula.
    def visitTff_and_formula(self, ctx: tptp_v7_0_0_0Parser.Tff_and_formulaContext):
        return self.visitFof_and_formula(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_unitary_formula.
    def visitTff_unitary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Tff_unitary_formulaContext
    ):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_quantified_formula.
    def visitTff_quantified_formula(
        self, ctx: tptp_v7_0_0_0Parser.Tff_quantified_formulaContext
    ):
        return self.visitThf_quantified_formula(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_variable_list.
    def visitTff_variable_list(self, ctx: tptp_v7_0_0_0Parser.Tff_variable_listContext):
        return self.visitThf_variable_list(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_variable.
    def visitTff_variable(self, ctx: tptp_v7_0_0_0Parser.Tff_variableContext):
        return self.visitThf_variable(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_typed_variable.
    def visitTff_typed_variable(
        self, ctx: tptp_v7_0_0_0Parser.Tff_typed_variableContext
    ):
        return self.visitThf_typed_variable(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_unary_formula.
    def visitTff_unary_formula(self, ctx: tptp_v7_0_0_0Parser.Tff_unary_formulaContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 2:
            return logic.UnaryFormula(
                self.visit(ctx.children[0]), self.visit(ctx.children[1])
            )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_atomic_formula.
    def visitTff_atomic_formula(
        self, ctx: tptp_v7_0_0_0Parser.Tff_atomic_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_conditional.
    def visitTff_conditional(self, ctx: tptp_v7_0_0_0Parser.Tff_conditionalContext):
        return self.visitThf_conditional(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let.
    def visitTff_let(self, ctx: tptp_v7_0_0_0Parser.Tff_letContext):
        return self.visitThf_let(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_term_defns.
    def visitTff_let_term_defns(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_term_defnsContext
    ):
        if len(ctx.children) == 1:
            return [self.visit_first(ctx)]
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_term_list.
    def visitTff_let_term_list(self, ctx: tptp_v7_0_0_0Parser.Tff_let_term_listContext):
        if len(ctx.children) == 1:
            return [self.visit_first(ctx)]
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[2]).append(self.visit(ctx.children[0]))
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_term_defn.
    def visitTff_let_term_defn(self, ctx: tptp_v7_0_0_0Parser.Tff_let_term_defnContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.ASSIGN,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_term_binding.
    def visitTff_let_term_binding(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_term_bindingContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_formula_defns.
    def visitTff_let_formula_defns(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_formula_defnsContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_formula_list.
    def visitTff_let_formula_list(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_formula_listContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_formula_defn.
    def visitTff_let_formula_defn(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_formula_defnContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_formula_binding.
    def visitTff_let_formula_binding(
        self, ctx: tptp_v7_0_0_0Parser.Tff_let_formula_bindingContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_sequent.
    def visitTff_sequent(self, ctx: tptp_v7_0_0_0Parser.Tff_sequentContext):
        return self.visitThf_sequent(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_formula_tuple.
    def visitTff_formula_tuple(self, ctx: tptp_v7_0_0_0Parser.Tff_formula_tupleContext):
        return self.visitFof_formula_tuple(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_formula_tuple_list.
    def visitTff_formula_tuple_list(
        self, ctx: tptp_v7_0_0_0Parser.Tff_formula_tuple_listContext
    ):
        return self.visitFof_formula_tuple_list(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_typed_atom.
    def visitTff_typed_atom(self, ctx: tptp_v7_0_0_0Parser.Tff_typed_atomContext):
        left = self.visit(ctx.children[0])
        if left == "(":
            return self.visit(ctx.children[1])
        else:
            return logic.TypedVariable(left, self.visit(ctx.children[2]))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_subtype.
    def visitTff_subtype(self, ctx: tptp_v7_0_0_0Parser.Tff_subtypeContext):
        return self.visitThf_subtype(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_top_level_type.
    def visitTff_top_level_type(
        self, ctx: tptp_v7_0_0_0Parser.Tff_top_level_typeContext
    ):
        return self.visitThf_top_level_type(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tf1_quantified_type.
    def visitTf1_quantified_type(
        self, ctx: tptp_v7_0_0_0Parser.Tf1_quantified_typeContext
    ):
        return logic.QuantifiedType(
            self.visit(ctx.children[0]), self.visit(ctx.children[5])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_monotype.
    def visitTff_monotype(self, ctx: tptp_v7_0_0_0Parser.Tff_monotypeContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_unitary_type.
    def visitTff_unitary_type(self, ctx: tptp_v7_0_0_0Parser.Tff_unitary_typeContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_atomic_type.
    def visitTff_atomic_type(self, ctx: tptp_v7_0_0_0Parser.Tff_atomic_typeContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return logic.FunctorExpression(
                self.visit(ctx.children[0]), self.visit(ctx.children[2])
            )
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_type_arguments.
    def visitTff_type_arguments(
        self, ctx: tptp_v7_0_0_0Parser.Tff_type_argumentsContext
    ):
        if len(ctx.children) == 1:
            return [self.visit_first(ctx)]
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[2]).append(self.visit(ctx.children[0]))
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_mapping_type.
    def visitTff_mapping_type(self, ctx: tptp_v7_0_0_0Parser.Tff_mapping_typeContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.ARROW,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_xprod_type.
    def visitTff_xprod_type(self, ctx: tptp_v7_0_0_0Parser.Tff_xprod_typeContext):
        return self.visitThf_xprod_type(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tcf_formula.
    def visitTcf_formula(self, ctx: tptp_v7_0_0_0Parser.Tcf_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tcf_logic_formula.
    def visitTcf_logic_formula(self, ctx: tptp_v7_0_0_0Parser.Tcf_logic_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tcf_quantified_formula.
    def visitTcf_quantified_formula(
        self, ctx: tptp_v7_0_0_0Parser.Tcf_quantified_formulaContext
    ):
        return logic.QuantifiedFormula(
            logic.Quantifier.UNIVERSAL,  # quantifier
            self.visit(ctx.children[2]),  # variable list
            self.visit(ctx.children[5]),  # formula
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_formula.
    def visitFof_formula(self, ctx: tptp_v7_0_0_0Parser.Fof_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_logic_formula.
    def visitFof_logic_formula(self, ctx: tptp_v7_0_0_0Parser.Fof_logic_formulaContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_binary_formula.
    def visitFof_binary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_binary_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_binary_nonassoc.
    def visitFof_binary_nonassoc(
        self, ctx: tptp_v7_0_0_0Parser.Fof_binary_nonassocContext
    ):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            self.visit(ctx.children[1]),
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_binary_assoc.
    def visitFof_binary_assoc(self, ctx: tptp_v7_0_0_0Parser.Fof_binary_assocContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_or_formula.
    def visitFof_or_formula(self, ctx: tptp_v7_0_0_0Parser.Fof_or_formulaContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.DISJUNCTION,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_and_formula.
    def visitFof_and_formula(self, ctx: tptp_v7_0_0_0Parser.Fof_and_formulaContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.CONJUNCTION,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_unitary_formula.
    def visitFof_unitary_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_unitary_formulaContext
    ):
        if len(ctx.children) == 1:
            # case: <fof_quantified_formula> | <fof_atomic_formula>
            return self.visit_first(ctx)
        else:
            # case: (<fof_logic_formula>)
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_quantified_formula.
    def visitFof_quantified_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_quantified_formulaContext
    ):
        return logic.QuantifiedFormula(
            self.visit(ctx.children[0]),  # quantifier
            self.visit(ctx.children[2]),  # variable list
            self.visit(ctx.children[5]),  # formula
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_variable_list.
    def visitFof_variable_list(self, ctx: tptp_v7_0_0_0Parser.Fof_variable_listContext):
        return [self.visit(ctx.children[i]) for i in range(0, len(ctx.children), 2)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_unary_formula.
    def visitFof_unary_formula(self, ctx: tptp_v7_0_0_0Parser.Fof_unary_formulaContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 2:
            return logic.UnaryFormula(
                self.visit(ctx.children[0]), self.visit(ctx.children[1])
            )
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_infix_unary.
    def visitFof_infix_unary(self, ctx: tptp_v7_0_0_0Parser.Fof_infix_unaryContext):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.NEQ,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_atomic_formula.
    def visitFof_atomic_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_atomic_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_plain_atomic_formula.
    def visitFof_plain_atomic_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_plain_atomic_formulaContext
    ):
        if len(ctx.children) == 1:
            # case: <proposition>
            r = self.visit_first(ctx)
            if isinstance(r, logic.FunctorExpression):
                r = logic.PredicateExpression(r.functor, r.arguments)
            return r
        else:
            # case: <predicate>(<fof_arguments>)
            return logic.PredicateExpression(
                self.visit(ctx.children[0]), self.visit(ctx.children[2])
            )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_atomic_formula.
    def visitFof_defined_atomic_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_defined_atomic_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_plain_formula.
    def visitFof_defined_plain_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_defined_plain_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_infix_formula.
    def visitFof_defined_infix_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_defined_infix_formulaContext
    ):
        return logic.BinaryFormula(
            self.visit(ctx.children[0]),
            logic.BinaryConnective.EQ,
            self.visit(ctx.children[2]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_system_atomic_formula.
    def visitFof_system_atomic_formula(
        self, ctx: tptp_v7_0_0_0Parser.Fof_system_atomic_formulaContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_plain_term.
    def visitFof_plain_term(self, ctx: tptp_v7_0_0_0Parser.Fof_plain_termContext):
        if len(ctx.children) == 1:
            # case: <constant>
            return self.visit_first(ctx)
        else:
            # case: <functor>(<fof_arguments>)
            return logic.FunctorExpression(
                self.visit(ctx.children[0]), self.visit(ctx.children[2])
            )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_term.
    def visitFof_defined_term(self, ctx: tptp_v7_0_0_0Parser.Fof_defined_termContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_atomic_term.
    def visitFof_defined_atomic_term(
        self, ctx: tptp_v7_0_0_0Parser.Fof_defined_atomic_termContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_defined_plain_term.
    def visitFof_defined_plain_term(
        self, ctx: tptp_v7_0_0_0Parser.Fof_defined_plain_termContext
    ):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 4:
            return logic.FunctorExpression(
                self.visit(ctx.children[0]), self.visit(ctx.children[2])
            )
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_system_term.
    def visitFof_system_term(self, ctx: tptp_v7_0_0_0Parser.Fof_system_termContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 4:
            return logic.FunctorExpression(
                self.visit(ctx.children[0]), self.visit(ctx.children[2])
            )
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_arguments.
    def visitFof_arguments(self, ctx: tptp_v7_0_0_0Parser.Fof_argumentsContext):
        return [self.visit(ctx.children[i]) for i in range(0, len(ctx.children), 2)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_term.
    def visitFof_term(self, ctx: tptp_v7_0_0_0Parser.Fof_termContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_function_term.
    def visitFof_function_term(self, ctx: tptp_v7_0_0_0Parser.Fof_function_termContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_conditional_term.
    def visitTff_conditional_term(
        self, ctx: tptp_v7_0_0_0Parser.Tff_conditional_termContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_let_term.
    def visitTff_let_term(self, ctx: tptp_v7_0_0_0Parser.Tff_let_termContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_tuple_term.
    def visitTff_tuple_term(self, ctx: tptp_v7_0_0_0Parser.Tff_tuple_termContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_sequent.
    def visitFof_sequent(self, ctx: tptp_v7_0_0_0Parser.Fof_sequentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_formula_tuple.
    def visitFof_formula_tuple(self, ctx: tptp_v7_0_0_0Parser.Fof_formula_tupleContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_formula_tuple_list.
    def visitFof_formula_tuple_list(
        self, ctx: tptp_v7_0_0_0Parser.Fof_formula_tuple_listContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#cnf_formula.
    def visitCnf_formula(self, ctx: tptp_v7_0_0_0Parser.Cnf_formulaContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#cnf_disjunction.
    def visitCnf_disjunction(self, ctx: tptp_v7_0_0_0Parser.Cnf_disjunctionContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        elif len(ctx.children) == 3:
            return logic.BinaryFormula(
                self.visit(ctx.children[0]),
                logic.BinaryConnective.DISJUNCTION,
                self.visit(ctx.children[2]),
            )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#cnf_literal.
    def visitCnf_literal(self, ctx: tptp_v7_0_0_0Parser.Cnf_literalContext):
        if len(ctx.children) == 1:
            return self.visit_first(ctx)
        else:
            return logic.UnaryFormula(
                logic.UnaryConnective.NEGATION, self.visit(ctx.children[1])
            )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_quantifier.
    def visitThf_quantifier(self, ctx: tptp_v7_0_0_0Parser.Thf_quantifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#th0_quantifier.
    def visitTh0_quantifier(self, ctx: tptp_v7_0_0_0Parser.Th0_quantifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#th1_quantifier.
    def visitTh1_quantifier(self, ctx: tptp_v7_0_0_0Parser.Th1_quantifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_pair_connective.
    def visitThf_pair_connective(
        self, ctx: tptp_v7_0_0_0Parser.Thf_pair_connectiveContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#thf_unary_connective.
    def visitThf_unary_connective(
        self, ctx: tptp_v7_0_0_0Parser.Thf_unary_connectiveContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#th1_unary_connective.
    def visitTh1_unary_connective(
        self, ctx: tptp_v7_0_0_0Parser.Th1_unary_connectiveContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#tff_pair_connective.
    def visitTff_pair_connective(
        self, ctx: tptp_v7_0_0_0Parser.Tff_pair_connectiveContext
    ):
        return self.visitChildren(ctx)

    _QUANTIFIER_MAP = {
        "!": logic.Quantifier.UNIVERSAL,
        "?": logic.Quantifier.EXISTENTIAL,
    }
    # Visit a parse tree produced by tptp_v7_0_0_0Parser#fof_quantifier.
    def visitFof_quantifier(self, ctx: tptp_v7_0_0_0Parser.Fof_quantifierContext):
        return self._QUANTIFIER_MAP[self.visit_first(ctx)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#binary_connective.
    def visitBinary_connective(self, ctx: tptp_v7_0_0_0Parser.Binary_connectiveContext):
        if len(ctx.children) == 1:
            connective = self.visit_first(ctx)
            if connective == "<=>":
                return logic.BinaryConnective.BIIMPLICATION
            elif connective == "=>":
                return logic.BinaryConnective.IMPLICATION
            elif connective == "<=":
                return logic.BinaryConnective.REVERSE_IMPLICATION
            elif connective == "<~>":
                return logic.BinaryConnective.SIMILARITY
            elif connective == "~&":
                return logic.BinaryConnective.NEGATED_CONJUNCTION
            elif connective == "~|":
                return logic.BinaryConnective.NEGATED_DISJUNCTION
            elif connective == "=":
                return logic.BinaryConnective.EQ
        raise NotImplementedError(connective)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#assoc_connective.
    def visitAssoc_connective(self, ctx: tptp_v7_0_0_0Parser.Assoc_connectiveContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#unary_connective.
    def visitUnary_connective(self, ctx: tptp_v7_0_0_0Parser.Unary_connectiveContext):
        connective = self.visit_first(ctx)
        if connective == "~":
            return logic.UnaryConnective.NEGATION
        raise NotImplementedError

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#type_constant.
    def visitType_constant(self, ctx: tptp_v7_0_0_0Parser.Type_constantContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#type_functor.
    def visitType_functor(self, ctx: tptp_v7_0_0_0Parser.Type_functorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_type.
    def visitDefined_type(self, ctx: tptp_v7_0_0_0Parser.Defined_typeContext):
        return logic.Type(self.visit_first(ctx))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#system_type.
    def visitSystem_type(self, ctx: tptp_v7_0_0_0Parser.System_typeContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#atom.
    def visitAtom(self, ctx: tptp_v7_0_0_0Parser.AtomContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#untyped_atom.
    def visitUntyped_atom(self, ctx: tptp_v7_0_0_0Parser.Untyped_atomContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_proposition.
    def visitDefined_proposition(
        self, ctx: tptp_v7_0_0_0Parser.Defined_propositionContext
    ):
        if isinstance(ctx.children[0], tptp_v7_0_0_0Parser.Defined_predicateContext):
            return self.visit_first(ctx)
        else:
            prop = self.visit_first(ctx)
            if prop == "$true":
                return logic.DefinedConstant.VERUM
            elif prop == "$false":
                return logic.DefinedConstant.FALSUM
        raise NotImplementedError

    _DEFINED_PREDICATE_MAP = {
        "$distinct": logic.DefinedPredicate.DISTINCT,
        "$less": logic.DefinedPredicate.LESS,
        "$lesseq": logic.DefinedPredicate.LESS_EQ,
        "$greater": logic.DefinedPredicate.GREATER,
        "$greatereq": logic.DefinedPredicate.GREATER_EQ,
        "$is_int": logic.DefinedPredicate.IS_INT,
        "$is_rat": logic.DefinedPredicate.IS_RAT,
        "$box_P": logic.DefinedPredicate.BOX_P,
        "$box_i": logic.DefinedPredicate.BOX_I,
        "$box_int": logic.DefinedPredicate.BOX_INT,
        "$box": logic.DefinedPredicate.BOX,
        "$dia_P": logic.DefinedPredicate.DIA_P,
        "$dia_i": logic.DefinedPredicate.DIA_I,
        "$dia_int": logic.DefinedPredicate.DIA_INT,
        "$dia": logic.DefinedPredicate.DIA,
    }

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_predicate.
    def visitDefined_predicate(self, ctx: tptp_v7_0_0_0Parser.Defined_predicateContext):
        if isinstance(ctx.children[0], tptp_v7_0_0_0Parser.Atomic_defined_wordContext):
            return self.visit_first(ctx)
        else:
            return self._DEFINED_PREDICATE_MAP[self.visit_first(ctx)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_infix_pred.
    def visitDefined_infix_pred(
        self, ctx: tptp_v7_0_0_0Parser.Defined_infix_predContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#constant.
    def visitConstant(self, ctx: tptp_v7_0_0_0Parser.ConstantContext):
        return logic.Constant(self.visit_first(ctx))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#functor.
    def visitFunctor(self, ctx: tptp_v7_0_0_0Parser.FunctorContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#system_constant.
    def visitSystem_constant(self, ctx: tptp_v7_0_0_0Parser.System_constantContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#system_functor.
    def visitSystem_functor(self, ctx: tptp_v7_0_0_0Parser.System_functorContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_constant.
    def visitDefined_constant(self, ctx: tptp_v7_0_0_0Parser.Defined_constantContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_functor.
    def visitDefined_functor(self, ctx: tptp_v7_0_0_0Parser.Defined_functorContext):
        f = self.visit_first(ctx)
        if f == "$true":
            return logic.DefinedConstant.VERUM
        elif f == "$false":
            return logic.DefinedConstant.FALSUM
        else:
            return f

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#defined_term.
    def visitDefined_term(self, ctx: tptp_v7_0_0_0Parser.Defined_termContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#variable.
    def visitVariable(self, ctx: tptp_v7_0_0_0Parser.VariableContext):
        return logic.Variable(self.visit_first(ctx))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#source.
    def visitSource(self, ctx: tptp_v7_0_0_0Parser.SourceContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#sources.
    def visitSources(self, ctx: tptp_v7_0_0_0Parser.SourcesContext):
        if len(ctx.children) == 1:
            return [self.visit(ctx.children[0])]
        elif len(ctx.children) == 3:
            return [self.visit(ctx.children[0])] + self.visit(ctx.children[2])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#dag_source.
    def visitDag_source(self, ctx: tptp_v7_0_0_0Parser.Dag_sourceContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_record.
    def visitInference_record(self, ctx: tptp_v7_0_0_0Parser.Inference_recordContext):
        return sources.InferenceSource(
            self.visit(ctx.children[1]),
            self.visit(ctx.children[3]),
            self.visit(ctx.children[5]),
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_rule.
    def visitInference_rule(self, ctx: tptp_v7_0_0_0Parser.Inference_ruleContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_parents.
    def visitInference_parents(self, ctx: tptp_v7_0_0_0Parser.Inference_parentsContext):
        if len(ctx.children) == 2:
            return []
        else:
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#parent_list.
    def visitParent_list(self, ctx: tptp_v7_0_0_0Parser.Parent_listContext):
        return self.visit_list(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#parent_info.
    def visitParent_info(self, ctx: tptp_v7_0_0_0Parser.Parent_infoContext):
        return self.visitChildren(ctx)[0]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#parent_details.
    def visitParent_details(self, ctx: tptp_v7_0_0_0Parser.Parent_detailsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#internal_source.
    def visitInternal_source(self, ctx: tptp_v7_0_0_0Parser.Internal_sourceContext):
        return sources.InternalSource(
            self.visit(ctx.children[1]), self.visit(ctx.children[2])
        )

    INTRO_TYPE_MAP = {
        "definition": sources.IntroductionType.DEFINITION,
        "axiom_of_choice": sources.IntroductionType.AXIOM_OF_CHOICE,
        "tautology": sources.IntroductionType.TAUTOLOGY,
        "assumption": sources.IntroductionType.ASSUMPTION,
        "avatar_definition": sources.IntroductionType.DEFINITION,
    }

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#intro_type.
    def visitIntro_type(self, ctx: tptp_v7_0_0_0Parser.Intro_typeContext):
        return self.INTRO_TYPE_MAP[self.visit_first(ctx)]

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#external_source.
    def visitExternal_source(self, ctx: tptp_v7_0_0_0Parser.External_sourceContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#file_source.
    def visitFile_source(self, ctx: tptp_v7_0_0_0Parser.File_sourceContext):
        return sources.FileSource(
            self.visit(ctx.children[1]), self.visit(ctx.children[2])
        )

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#file_info.
    def visitFile_info(self, ctx: tptp_v7_0_0_0Parser.File_infoContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#theory.
    def visitTheory(self, ctx: tptp_v7_0_0_0Parser.TheoryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#theory_name.
    def visitTheory_name(self, ctx: tptp_v7_0_0_0Parser.Theory_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#creator_source.
    def visitCreator_source(self, ctx: tptp_v7_0_0_0Parser.Creator_sourceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#creator_name.
    def visitCreator_name(self, ctx: tptp_v7_0_0_0Parser.Creator_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#optional_info.
    def visitOptional_info(self, ctx: tptp_v7_0_0_0Parser.Optional_infoContext):
        return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#useful_info.
    def visitUseful_info(self, ctx: tptp_v7_0_0_0Parser.Useful_infoContext):
        if len(ctx.children) <= 2:
            return []
        else:
            return self.visit(ctx.children[1])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#info_items.
    def visitInfo_items(self, ctx: tptp_v7_0_0_0Parser.Info_itemsContext):
        return self.visit_list(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#info_item.
    def visitInfo_item(self, ctx: tptp_v7_0_0_0Parser.Info_itemContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#formula_item.
    def visitFormula_item(self, ctx: tptp_v7_0_0_0Parser.Formula_itemContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#description_item.
    def visitDescription_item(self, ctx: tptp_v7_0_0_0Parser.Description_itemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#iquote_item.
    def visitIquote_item(self, ctx: tptp_v7_0_0_0Parser.Iquote_itemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_item.
    def visitInference_item(self, ctx: tptp_v7_0_0_0Parser.Inference_itemContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_status.
    def visitInference_status(self, ctx: tptp_v7_0_0_0Parser.Inference_statusContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#status_value.
    def visitStatus_value(self, ctx: tptp_v7_0_0_0Parser.Status_valueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#inference_info.
    def visitInference_info(self, ctx: tptp_v7_0_0_0Parser.Inference_infoContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#assumptions_record.
    def visitAssumptions_record(
        self, ctx: tptp_v7_0_0_0Parser.Assumptions_recordContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#refutation.
    def visitRefutation(self, ctx: tptp_v7_0_0_0Parser.RefutationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#new_symbol_record.
    def visitNew_symbol_record(self, ctx: tptp_v7_0_0_0Parser.New_symbol_recordContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#new_symbol_list.
    def visitNew_symbol_list(self, ctx: tptp_v7_0_0_0Parser.New_symbol_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#principal_symbol.
    def visitPrincipal_symbol(self, ctx: tptp_v7_0_0_0Parser.Principal_symbolContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#include.
    def visitInclude(self, ctx: tptp_v7_0_0_0Parser.IncludeContext):
        return logic.Import(self.visit(ctx.children[1]))

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#formula_selection.
    def visitFormula_selection(self, ctx: tptp_v7_0_0_0Parser.Formula_selectionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#name_list.
    def visitName_list(self, ctx: tptp_v7_0_0_0Parser.Name_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#general_term.
    def visitGeneral_term(self, ctx: tptp_v7_0_0_0Parser.General_termContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#general_data.
    def visitGeneral_data(self, ctx: tptp_v7_0_0_0Parser.General_dataContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#general_function.
    def visitGeneral_function(self, ctx: tptp_v7_0_0_0Parser.General_functionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#formula_data.
    def visitFormula_data(self, ctx: tptp_v7_0_0_0Parser.Formula_dataContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#general_list.
    def visitGeneral_list(self, ctx: tptp_v7_0_0_0Parser.General_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#general_terms.
    def visitGeneral_terms(self, ctx: tptp_v7_0_0_0Parser.General_termsContext):
        return self.visit_list(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#name.
    def visitName(self, ctx: tptp_v7_0_0_0Parser.NameContext):
        return self.visit(ctx.children[0])

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#atomic_word.
    def visitAtomic_word(self, ctx: tptp_v7_0_0_0Parser.Atomic_wordContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#atomic_defined_word.
    def visitAtomic_defined_word(
        self, ctx: tptp_v7_0_0_0Parser.Atomic_defined_wordContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#atomic_system_word.
    def visitAtomic_system_word(
        self, ctx: tptp_v7_0_0_0Parser.Atomic_system_wordContext
    ):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#number.
    def visitNumber(self, ctx: tptp_v7_0_0_0Parser.NumberContext):
        return self.visit_first(ctx)

    # Visit a parse tree produced by tptp_v7_0_0_0Parser#file_name.
    def visitFile_name(self, ctx: tptp_v7_0_0_0Parser.File_nameContext):
        return self.visit(ctx.children[0])

    """def aggregateResult(self, aggregate, nextResult):
        if aggregate is None:
            return [nextResult]
        return aggregate.append(nextResult)"""
