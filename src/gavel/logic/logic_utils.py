import itertools
from queue import Queue
from typing import Optional, Set

import gavel.logic.logic as logic


# basic functionality for manipulating FOL formulas


def binary_to_nary(
    formula: logic.LogicExpression, connective: logic.BinaryConnective
) -> logic.NaryFormula:
    assert connective.is_associative()
    if isinstance(formula, logic.BinaryFormula) and formula.operator == connective:
        return logic.NaryFormula(
            connective,
            list(itertools.chain(
                binary_to_nary(formula.left, connective).formulae,
                binary_to_nary(formula.right, connective).formulae,
            )),
        )
    if isinstance(formula, logic.NaryFormula) and formula.operator == connective:
        return logic.NaryFormula(
            connective,
            [
                f
                for sub in formula.formulae
                for f in binary_to_nary(sub, connective).formulae
            ],
        )
    else:
        return logic.NaryFormula(connective, [formula])


def get_vars_in_formula(formula: logic.LogicElement) -> Set[logic.Variable]:
    if isinstance(formula, logic.Variable):
        return {formula}
    elif isinstance(formula, logic.PredicateExpression):
        return set(arg for arg in formula.arguments if isinstance(arg, logic.Variable))
    elif isinstance(formula, logic.BinaryFormula):
        return get_vars_in_formula(formula.left).union(
            get_vars_in_formula(formula.right)
        )
    elif isinstance(formula, logic.UnaryFormula) or isinstance(
        formula, logic.QuantifiedFormula
    ):
        return get_vars_in_formula(formula.formula)
    elif isinstance(formula, logic.NaryFormula):
        variables = [get_vars_in_formula(f) for f in formula.formulae]
        variables = [v for v in variables if v is not None]
        if len(variables) > 0:
            try:
                return set.union(*variables)
            except TypeError:
                return set()
    else:
        return set()


def substitute_var_in_formula(
    formula: logic.LogicElement, var: Optional[logic.Variable], ind
):
    """Replace every occurrence of variable var with ind. If var is None, replace all variables with ind"""
    if isinstance(formula, logic.NaryFormula):
        return logic.NaryFormula(
            formula.operator,
            [substitute_var_in_formula(f, var, ind) for f in formula.formulae],
        )
    elif isinstance(formula, logic.PredicateExpression):
        return logic.PredicateExpression(
            formula.predicate,
            [
                (
                    ind
                    if isinstance(arg, logic.Variable) and (not var or arg == var)
                    else arg
                )
                for arg in formula.arguments
            ],
        )
    elif isinstance(formula, logic.UnaryFormula):
        return logic.UnaryFormula(
            formula.connective, substitute_var_in_formula(formula.formula, var, ind)
        )
    elif isinstance(formula, logic.QuantifiedFormula):
        variables = [arg for arg in formula.variables if arg != var]
        return logic.QuantifiedFormula(
            formula.quantifier,
            variables,
            substitute_var_in_formula(formula.formula, var, ind),
        )
    elif isinstance(formula, logic.BinaryFormula):
        left = substitute_var_in_formula(formula.left, var, ind)
        right = substitute_var_in_formula(formula.right, var, ind)
        return logic.BinaryFormula(left, formula.operator, right)
    elif isinstance(formula, logic.Variable):
        return ind if not var or formula == var else formula
    return formula


def replace_predicate_symbol(formula: logic.LogicElement, old: str, new: str):
    """Replace every occurrence of a predicate symbol in a given formula"""
    if isinstance(formula, logic.PredicateExpression) and formula.predicate == old:
        formula.predicate = new
    elif isinstance(formula, logic.UnaryFormula):
        formula.formula = replace_predicate_symbol(formula.formula, old, new)
    elif isinstance(formula, logic.QuantifiedFormula):
        formula.formula = replace_predicate_symbol(formula.formula, old, new)
    elif isinstance(formula, logic.BinaryFormula):
        formula.left = replace_predicate_symbol(formula.left, old, new)
        formula.right = replace_predicate_symbol(formula.right, old, new)
    elif isinstance(formula, logic.NaryFormula):
        formula.formulae = [
            replace_predicate_symbol(f, old, new) for f in formula.formulae
        ]
    return formula


def is_atom_formula(formula: logic.LogicExpression):
    if not isinstance(formula, logic.PredicateExpression):
        return False
    # allow integers as terms
    return isinstance(formula.arguments, logic.TermExpression) or all(
        isinstance(t, logic.TermExpression) or isinstance(t, int)
        for t in formula.arguments
    )


def is_literal(formula: logic.LogicExpression):
    return (
        is_atom_formula(formula)
        or (
            isinstance(formula, logic.UnaryFormula) and is_atom_formula(formula.formula)
        )
        or (
            isinstance(formula, logic.BinaryFormula)
            and (
                formula.operator == logic.BinaryConnective.EQ
                or formula.operator == logic.BinaryConnective.NEQ
            )
        )
    )


def convert_biimplication_to_cnf(formula: logic.BinaryFormula):
    """a <-> b <=> (~a | b) & (~b | a)"""
    assert formula.operator == logic.BinaryConnective.BIIMPLICATION
    return logic.BinaryFormula(
        logic.BinaryFormula(
            logic.UnaryFormula(logic.UnaryConnective.NEGATION, formula.left),
            logic.BinaryConnective.DISJUNCTION,
            formula.right,
        ),
        logic.BinaryConnective.CONJUNCTION,
        logic.BinaryFormula(
            formula.left,
            logic.BinaryConnective.DISJUNCTION,
            logic.UnaryFormula(logic.UnaryConnective.NEGATION, formula.right),
        ),
    )


def convert_implication_to_disjunction(formula: logic.BinaryFormula):
    """a -> b <=> ~a | b"""
    assert formula.operator == logic.BinaryConnective.IMPLICATION
    return logic.BinaryFormula(
        logic.UnaryFormula(logic.UnaryConnective.NEGATION, formula.left),
        logic.BinaryConnective.DISJUNCTION,
        formula.right,
    )


def convert_to_nnf(formula: logic.LogicExpression):
    """Replace all <-> with (~a|b)&(~b|a), all -> with (~a|b), all ~(a!=b) with a=b, all ~(a=b) with a!=b,
    all ~(a|b) with (~a&~b), all ~(a&b) with (~a|~b), all ~![] with ?[]~, all ~?[] with ?[]~, all ~~a with a.
    Resulting formula will only have |, & and ~ operations and ~ only for literals"""
    if (
        isinstance(formula, logic.UnaryFormula)
        and formula.connective == logic.UnaryConnective.NEGATION
    ):
        if isinstance(formula.formula, logic.QuantifiedFormula):
            if formula.formula.quantifier == logic.Quantifier.EXISTENTIAL:
                quantifier = logic.Quantifier.UNIVERSAL
            else:
                quantifier = logic.Quantifier.EXISTENTIAL
            return logic.QuantifiedFormula(
                quantifier,
                formula.formula.variables,
                convert_to_nnf(
                    logic.UnaryFormula(
                        logic.UnaryConnective.NEGATION, formula.formula.formula
                    )
                ),
            )
        elif (
            isinstance(formula.formula, logic.BinaryFormula)
            and formula.formula.operator == logic.BinaryConnective.BIIMPLICATION
        ):
            return convert_to_nnf(
                logic.UnaryFormula(
                    logic.UnaryConnective.NEGATION,
                    convert_biimplication_to_cnf(formula.formula),
                )
            )
        elif (
            isinstance(formula.formula, logic.BinaryFormula)
            and formula.formula.operator == logic.BinaryConnective.IMPLICATION
        ):
            return convert_to_nnf(
                logic.UnaryFormula(
                    logic.UnaryConnective.NEGATION,
                    convert_implication_to_disjunction(formula.formula),
                )
            )
        elif isinstance(formula.formula, logic.BinaryFormula) or isinstance(
            formula.formula, logic.NaryFormula
        ):
            if formula.formula.operator == logic.BinaryConnective.DISJUNCTION:
                operator = logic.BinaryConnective.CONJUNCTION
            elif formula.formula.operator == logic.BinaryConnective.CONJUNCTION:
                operator = logic.BinaryConnective.DISJUNCTION
            elif formula.formula.operator == logic.BinaryConnective.EQ:
                assert isinstance(formula.formula, logic.BinaryFormula)
                return logic.BinaryFormula(
                    formula.formula.left,
                    logic.BinaryConnective.NEQ,
                    formula.formula.right,
                )
            elif formula.formula.operator == logic.BinaryConnective.NEQ:
                assert isinstance(formula.formula, logic.BinaryFormula)
                return logic.BinaryFormula(
                    formula.formula.left,
                    logic.BinaryConnective.EQ,
                    formula.formula.right,
                )
            else:
                raise NotImplementedError
            if isinstance(formula.formula, logic.BinaryFormula):
                return logic.BinaryFormula(
                    convert_to_nnf(
                        logic.UnaryFormula(
                            logic.UnaryConnective.NEGATION, formula.formula.left
                        )
                    ),
                    operator,
                    convert_to_nnf(
                        logic.UnaryFormula(
                            logic.UnaryConnective.NEGATION, formula.formula.right
                        )
                    ),
                )
            else:
                return logic.NaryFormula(
                    operator,
                    [
                        convert_to_nnf(
                            logic.UnaryFormula(logic.UnaryConnective.NEGATION, f)
                        )
                        for f in formula.formula.formulae
                    ],
                )
        elif (
            isinstance(formula.formula, logic.UnaryFormula)
            and formula.formula.connective == logic.UnaryConnective.NEGATION
        ):
            return convert_to_nnf(formula.formula.formula)
        else:
            return formula
    else:
        if isinstance(formula, logic.QuantifiedFormula):
            return logic.QuantifiedFormula(
                formula.quantifier, formula.variables, convert_to_nnf(formula.formula)
            )
        elif (
            isinstance(formula, logic.BinaryFormula)
            and formula.operator == logic.BinaryConnective.BIIMPLICATION
        ):
            return convert_to_nnf(convert_biimplication_to_cnf(formula))
        elif (
            isinstance(formula, logic.BinaryFormula)
            and formula.operator == logic.BinaryConnective.IMPLICATION
        ):
            return convert_to_nnf(convert_implication_to_disjunction(formula))
        elif isinstance(formula, logic.BinaryFormula):
            return logic.BinaryFormula(
                convert_to_nnf(formula.left),
                formula.operator,
                convert_to_nnf(formula.right),
            )
        elif isinstance(formula, logic.NaryFormula):
            return logic.NaryFormula(
                formula.operator, [convert_to_nnf(f) for f in formula.formulae]
            )
        else:
            return formula


def convert_to_cnf(formula: logic.LogicExpression) -> logic.NaryFormula:
    """Assumes no quantifiers"""
    formula = convert_to_nnf(formula)
    clauses = []
    unprocessed_clauses = Queue()
    unprocessed_clauses.put(formula)

    while not unprocessed_clauses.empty():
        clause = unprocessed_clauses.get()
        if isinstance(clause, logic.NaryFormula) or isinstance(
            clause, logic.BinaryFormula
        ):
            # nested conjunctions: resolve
            if clause.operator == logic.BinaryConnective.CONJUNCTION:
                if isinstance(clause, logic.BinaryFormula):
                    unprocessed_clauses.put(formula.left)
                    unprocessed_clauses.put(formula.right)
                else:
                    assert isinstance(clause, logic.NaryFormula)
                    for f in clause.formulae:
                        unprocessed_clauses.put(f)
            # disjunctions: apply cnf recursively, then distribute
            # i.e. [(A|B)&(C|D)] | [(E|F)&(G|H)] -> (A|B|E|F)&(A|B|G|H)&(C|D|E|F)&(C|D|G|H)
            elif clause.operator == logic.BinaryConnective.DISJUNCTION:
                if isinstance(clause, logic.BinaryFormula):
                    disj_parts = [clause.left, clause.right]
                else:
                    assert isinstance(clause, logic.NaryFormula)
                    disj_parts = clause.formulae
                disj_parts = [convert_to_cnf(p).formulae for p in disj_parts]
                for combination in itertools.product(*disj_parts):
                    clause_elements = []
                    for c in combination:
                        clause_elements += c.formulae
                    clauses.append(
                        logic.NaryFormula(
                            logic.BinaryConnective.DISJUNCTION, clause_elements
                        )
                    )
            else:
                clauses.append(
                    logic.NaryFormula(logic.BinaryConnective.DISJUNCTION, [clause])
                )
        else:
            clauses.append(
                logic.NaryFormula(logic.BinaryConnective.DISJUNCTION, [clause])
            )

    return logic.NaryFormula(logic.BinaryConnective.CONJUNCTION, clauses)
