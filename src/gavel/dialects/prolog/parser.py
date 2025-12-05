"""
Prolog to First-Order Logic Parser

This module provides a parser that converts Prolog syntax to First-Order Logic (FOL)
formulas using the Lark parsing library.

Prolog clauses are translated to FOL as follows:
- Facts: p(X) --> p(X) (simple predicate)
- Rules: p(X) :- q(X), r(X) --> forall X: (q(X) & r(X)) => p(X)
- Queries: ?- p(X) --> exists X: p(X) (treated as conjectures)
"""

import os
import re
from typing import Iterable
from itertools import chain

from lark import Lark, Tree, Transformer

from gavel.dialects.base.parser import LogicParser, StringBasedParser
from gavel.logic import logic
from gavel.logic.problem import AnnotatedFormula, FormulaRole, Import


class PrologTransformer(Transformer):
    """
    Transformer that converts Prolog parse trees to FOL LogicElement objects.
    
    This follows the standard Prolog to FOL translation:
    - A fact 'p(a).' becomes the FOL formula p(a)
    - A rule 'p(X) :- q(X), r(X).' becomes ∀X: (q(X) ∧ r(X)) → p(X)
    - A query '?- p(X).' becomes ∃X: p(X) (conjecture)
    """
    
    def __init__(self):
        super().__init__()
        self._clause_counter = 0
    
    def visit(self, obj, **kwargs):
        """Visit a tree node and call the appropriate visitor method."""
        if isinstance(obj, str):
            return obj
        meth = getattr(self, f"visit_{obj.data}", None)
        if meth is None:
            raise Exception(f"Visitor 'visit_{obj.data}' not found for {type(obj)}")
        return meth(obj, **kwargs)
    
    def start(self, items):
        for c in items:
            yield self.visit(c)

    def visit_clause(self, obj, **kwargs):
        """Process a clause, which can be a fact or rule."""
        return self.visit(obj.children[0], **kwargs)
    
    def visit_fact(self, obj, **kwargs):
        """
        Process a fact: p(X).
        
        A fact is simply a predicate that is always true.
        Returns an AnnotatedFormula with AXIOM role.
        """
        predicate = obj.children[0]
        self._clause_counter += 1
        
        # Extract free variables from the predicate
        free_vars = self._collect_variables(predicate)
        
        # If there are free variables, universally quantify them
        if free_vars:
            formula = logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable(v) for v in sorted(free_vars)],
                formula=predicate
            )
        else:
            formula = predicate
        
        return AnnotatedFormula(
            logic="fol",
            name=f"fact_{self._clause_counter}",
            role=FormulaRole.AXIOM,
            formula=formula
        )
    
    def visit_rule(self, obj, **kwargs):
        """
        Process a rule: head :- body.
        
        A rule 'p(X) :- q(X), r(X).' is translated to:
        ∀X: (q(X) ∧ r(X)) → p(X)
        
        Returns an AnnotatedFormula with AXIOM role.
        """
        head = obj.children[0]  # This is the result from predicate
        body_predicates = obj.children[1]  # This is the result from predicate_list
        self._clause_counter += 1
        
        # Combine body predicates with conjunction
        if len(body_predicates) == 1:
            body = body_predicates[0]
        else:
            body = logic.NaryFormula(
                operator=logic.BinaryConnective.CONJUNCTION,
                formulae=body_predicates)
            
        
        # Create implication: body => head
        implication = logic.BinaryFormula(
            left=body,
            operator=logic.BinaryConnective.IMPLICATION,
            right=head
        )
        
        # Collect all free variables
        free_vars = self._collect_variables(implication)
        
        # Universally quantify all variables
        if free_vars:
            formula = logic.QuantifiedFormula(
                quantifier=logic.Quantifier.UNIVERSAL,
                variables=[logic.Variable(v) for v in sorted(free_vars)],
                formula=implication
            )
        else:
            formula = implication
        
        return AnnotatedFormula(
            logic="fol",
            name=f"rule_{self._clause_counter}",
            role=FormulaRole.AXIOM,
            formula=formula
        )
    
    def visit_query(self, obj, **kwargs):
        """
        Process a query: ?- p(X).
        
        A query is treated as a conjecture (goal to prove).
        '?- p(X).' becomes ∃X: p(X)
        
        Returns an AnnotatedFormula with CONJECTURE role.
        """
        predicates = obj.children[0]  # Result from predicate_list
        self._clause_counter += 1
        
        # Combine predicates with conjunction if multiple
        if len(predicates) == 1:
            formula_body = predicates[0]
        else:
            formula_body = logic.NaryFormula(
                operator=logic.BinaryConnective.CONJUNCTION,
                formulae=predicates)
        
        # Collect free variables
        free_vars = self._collect_variables(formula_body)
        
        # Existentially quantify variables
        if free_vars:
            formula = logic.QuantifiedFormula(
                quantifier=logic.Quantifier.EXISTENTIAL,
                variables=[logic.Variable(v) for v in sorted(free_vars)],
                formula=formula_body
            )
        else:
            formula = formula_body
        
        return AnnotatedFormula(
            logic="fol",
            name=f"query_{self._clause_counter}",
            role=FormulaRole.CONJECTURE,
            formula=formula
        )
    
    def predicate_list(self, items):
        """Process a list of predicates (conjunction in body or query)."""
        return [self.visit(item) if isinstance(item, Tree) else item for item in items]
    
    def predicate(self, items):
        """
        Process a predicate.
        
        Can be:
        - atom (propositional predicate)
        - atom(term1, term2, ...) (predicate with arguments)
        """
        atom_name = items[0]
        
        if len(items) == 1:
            # Propositional predicate (no arguments)
            return logic.PredicateExpression(
                predicate=atom_name,
                arguments=[]
            )
        else:
            # Predicate with arguments
            terms = items[1]
            return logic.PredicateExpression(
                predicate=atom_name,
                arguments=terms
            )
    
    def term_list(self, items):
        """Process a list of terms."""
        return [self.visit(item) if isinstance(item, Tree) else item for item in items]
    
    def structure(self, items):
        """
        Process a structure (functor with arguments).
        
        In FOL, this becomes a FunctorExpression.
        """
        functor = items[0]
        terms = items[1]
        
        return logic.FunctorExpression(
            functor=functor,
            arguments=terms
        )
    
    def list_term(self, items):
        """
        Process a list term.
        
        Prolog lists can be represented as nested structures using a list functor.
        [a, b, c] becomes cons(a, cons(b, cons(c, nil)))
        [H|T] becomes cons(H, T)
        """
        if len(items) == 0:
            # Empty list []
            return logic.Constant("nil")
        else:
            return self.visit(items[0])
    
    def list_elements(self, items):
        """
        Process list elements.
        
        Build cons structures: [a, b | T] becomes cons(a, cons(b, T))
        """
        if len(items) == 0:
            return logic.Constant("nil")
        
        # Check if there's a tail (|T pattern)
        has_tail = False
        elements = []
        tail = None
        
        for item in items:
            if isinstance(item, Tree):
                elements.append(self.visit(item))
            else:
                elements.append(item)
        
        # Build from right to left
        # If last element should be tail, handle it differently
        # For now, simple implementation: all elements in sequence
        result = logic.Constant("nil")
        for elem in reversed(elements):
            result = logic.FunctorExpression(
                functor="cons",
                arguments=[elem, result]
            )
        
        return result
    
    def atom(self, items):
        """Process an atom (constant symbol)."""
        atom_str = str(items[0])
        # Remove quotes if it's a quoted atom
        if atom_str.startswith("'") and atom_str.endswith("'"):
            atom_str = atom_str[1:-1]
        return atom_str
    
    def variable(self, items):
        """Process a variable."""
        var_name = str(items[0])
        return logic.Variable(var_name)
    
    def number(self, items):
        """Process a number constant."""
        return logic.DefinedConstant(str(items[0]))
    
    def comment(self, items):
        """Ignore comments."""
        return None
    
    def _collect_variables(self, element):
        """
        Recursively collect all variable names from a logic element.
        
        Returns a set of variable name strings.
        """
        variables = set()
        
        if isinstance(element, logic.Variable):
            variables.add(element.symbol)
        elif isinstance(element, logic.PredicateExpression):
            for arg in element.arguments:
                variables.update(self._collect_variables(arg))
        elif isinstance(element, logic.FunctorExpression):
            for arg in element.arguments:
                variables.update(self._collect_variables(arg))
        elif isinstance(element, logic.BinaryFormula):
            variables.update(self._collect_variables(element.left))
            variables.update(self._collect_variables(element.right))
        elif isinstance(element, logic.UnaryFormula):
            variables.update(self._collect_variables(element.formula))
        elif isinstance(element, logic.QuantifiedFormula):
            # Don't collect bound variables
            bound_vars = {v.symbol for v in element.variables}
            free_in_body = self._collect_variables(element.formula)
            variables.update(free_in_body - bound_vars)
        
        return variables


class PrologParser(LogicParser, StringBasedParser):
    """
    Parser for Prolog programs that converts them to First-Order Logic.
    
    This parser uses a Lark grammar to parse Prolog syntax and a transformer
    to convert the parsed structure into FOL formulas represented as LogicElement objects.
    
    Usage:
        parser = PrologParser()
        results = parser.parse("father(john, mary). ?- father(X, mary).")
    """
    
    def __init__(self):
        """Initialize the parser with the Prolog grammar."""
        grammar_path = os.path.join(os.path.dirname(__file__), "prolog.lark")
        self.lark_parser = Lark.open(
            grammar_path,
            start=["start"],
            parser="lalr",
            transformer=PrologTransformer()
        )
    
    def parse(self, structure: str, *args, **kwargs) -> Iterable[logic.LogicElement]:
        """
        Parse a Prolog program string into FOL formulas.
        
        Parameters
        ----------
        structure : str
            A Prolog program as a string
            
        Returns
        -------
        Iterable[LogicElement]
            A list of AnnotatedFormula objects representing the program in FOL
            
        Examples
        --------
        >>> parser = PrologParser()
        >>> results = parser.parse("parent(tom, bob). parent(bob, ann).")
        >>> len(results)
        2
        """
        try:
            return list(self.lark_parser.parse(structure))
        except Exception as e:
            raise Exception(str(e))
        
    
    def is_valid(self, inp: str) -> bool:
        """
        Check if a string is valid Prolog syntax.
        
        Parameters
        ----------
        inp : str
            String to validate
            
        Returns
        -------
        bool
            True if the input is valid Prolog, False otherwise
        """
        try:
            self.parse(inp)
            return True
        except:
            return False

if __name__ == "__main__":
    parser = PrologParser()
    prolog_program = """
    father(tom, bob).
    parent(X,Y) :- father(X,Y).
    ?- parent(tom, Y).
    """
    results = parser.parse(prolog_program)
    for formula in results:
        print(formula)