import os
import pickle as pkl
import re
import sys
from typing import Iterable

import requests

try:
    from antlr4 import CommonTokenStream
    from antlr4 import InputStream
except:
    SUPPORTS_ANTLR = False
else:
    SUPPORTS_ANTLR = True

import gavel.config.settings as settings
import gavel.dialects.db.structures as db
from gavel.config import settings as settings
from gavel.dialects.base.parser import LogicParser, Parseable, Target, StringBasedParser
from gavel.dialects.base.parser import ParserException
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.base.parser import ProofParser
from gavel.dialects.db.compiler import DBCompiler
from gavel.dialects.db.connection import get_or_create
from gavel.dialects.db.connection import get_or_None
from gavel.dialects.db.connection import with_session
from gavel.dialects.tptp.sources import InferenceSource
from gavel.dialects.tptp.sources import Input
from gavel.dialects.tptp.sources import InternalSource
from gavel.logic import logic
from gavel.logic import problem
from gavel.logic.logic import LogicElement
from gavel.logic.problem import AnnotatedFormula
from gavel.logic.problem import FormulaRole
from gavel.logic.problem import Problem
from gavel.logic.proof import Axiom
from gavel.logic.proof import Inference
from gavel.logic.proof import Introduction
from gavel.logic.proof import LinearProof
from gavel.logic.proof import ProofStep

if SUPPORTS_ANTLR:
    from .antlr4.flattening import FOFFlatteningVisitor
    from .antlr4.tptp_v7_0_0_0Lexer import tptp_v7_0_0_0Lexer
    from .antlr4.tptp_v7_0_0_0Parser import tptp_v7_0_0_0Parser

from lark import Lark, Tree

sys.setrecursionlimit(10000)

form_expression = re.compile(r"^(?!%|\n)(?P<logic>[^(]*)\([^.]*\)\.\S*$")

_BINARY_CONNECTIVE_MAP = {
    "&": logic.BinaryConnective.CONJUNCTION,
    "|": logic.BinaryConnective.DISJUNCTION,
    "=>": logic.BinaryConnective.IMPLICATION,
    "<=>": logic.BinaryConnective.BIIMPLICATION,
    "<=": logic.BinaryConnective.REVERSE_IMPLICATION,
    "<~>": logic.BinaryConnective.SIMILARITY,
    "~&": logic.BinaryConnective.NEGATED_CONJUNCTION,
    "~|": logic.BinaryConnective.NEGATED_DISJUNCTION,
    "=": logic.BinaryConnective.EQ,
    "!=": logic.BinaryConnective.NEQ,
    "@": logic.BinaryConnective.APPLY,
    "*": logic.BinaryConnective.PRODUCT,
    "+": logic.BinaryConnective.UNION,
    "-->": logic.BinaryConnective.GENTZEN_ARROW,
    ":=": logic.BinaryConnective.ASSIGN,
    ">": logic.BinaryConnective.ARROW,
}

with open(os.path.join(os.path.dirname(__file__), "tptp.lark")) as gf:
    lark_grammar = Lark(gf.read(), start=["start", "tptp_line"])


def _balance_binary_tree(obj, skip_connective=True, **kwargs):
    if len(obj.children) > 2:
        split_point = len(obj.children) // 2
        if skip_connective:
            cl = obj.children[:split_point]
            cr = obj.children[split_point:]
        else:
            # It the split marker is on an operator everything is fine.
            # Otherwise move it
            if not (
                isinstance(obj.children[split_point], str)
                and obj.children[split_point] in _BINARY_CONNECTIVE_MAP
            ):
                split_point -= 1
            connective = obj.children[split_point]
            cl = obj.children[:split_point]
            cr = obj.children[split_point + 1 :]

        tl = Tree(data=obj.data, children=cl)
        tr = Tree(data=obj.data, children=cr)
        l = _balance_binary_tree(tl, skip_connective=skip_connective, **kwargs)
        r = _balance_binary_tree(tr, skip_connective=skip_connective, **kwargs)
        if skip_connective:
            return Tree(data=obj.data, children=[l, r])
        else:
            return Tree(data=obj.data, children=[l, connective, r])
    else:
        return obj


def _recursive_binary(skip_connective=True):
    def wrapper(f):
        def inner(self, obj, **kwargs):
            if len(obj.children) == 1:
                return self.visit(obj.children[0], **kwargs)
            else:
                return f(
                    self,
                    _balance_binary_tree(obj, skip_connective=skip_connective),
                    **kwargs
                )

        return inner

    return wrapper


class TPTPParser(LogicParser, StringBasedParser):
    def is_valid(self, inp: str) -> bool:
        pass

    def parse(self, structure: Parseable, *args, **kwargs) -> Target:
        return self.visit(structure)

    def load_single_from_string(self, string: str, *args, **kwargs):
        r = lark_grammar.parse(string, start="tptp_line")
        return r

    def visit(self, obj: Tree, **kwargs):
        if isinstance(obj, str):
            return obj
        meth = getattr(self, "visit_%s" % obj.data, None)

        if meth is None:
            raise Exception(
                "Visitor '{name}' not found for {cls}".format(
                    name=obj.data, cls=type(obj)
                )
            )
        return meth(obj, **kwargs)

    def visit_start(self, obj, **kwargs):
        assert len(obj.children) == 1
        return self.visit(obj.children[0], **kwargs)

    def visit_tptp_line(self, obj, **kwargs):
        return self.visit(obj.children[0], **kwargs)

    def visit_annotated_formula(self, obj, **kwargs):
        return problem.AnnotatedFormula(
            logic=obj.children[0],
            name=obj.children[1],
            role=self._ROLE_MAP[obj.children[2]],
            formula=self.visit(obj.children[3], **kwargs),
        )

    def visit_formula(self, obj, **kwargs):
        return self.visit(obj.children[0], **kwargs)

    def visit_functor_term(self, obj, term_level=False, **kwargs):
        c0 = obj.children[0]
        is_defined = c0.startswith("$")
        if len(obj.children) > 1:
            if term_level:
                return logic.FunctorExpression(
                    functor=c0,
                    arguments=[
                        self.visit(c, term_level=term_level, **kwargs)
                        for c in obj.children[1:]
                    ],
                )
            else:
                p = self._DEFINED_PREDICATE_MAP[c0] if is_defined else c0
                return logic.PredicateExpression(
                    predicate=p,
                    arguments=[
                        self.visit(c, term_level=True, **kwargs)
                        for c in obj.children[1:]
                    ],
                )
        else:
            assert len(obj.children) == 1 and isinstance(obj.children[0], str)
            if is_defined:
                if c0 == "$true":
                    return logic.DefinedConstant.VERUM
                elif c0 == "$false":
                    return logic.DefinedConstant.FALSUM
                else:
                    return logic.DefinedConstant(c0)
            else:
                if c0[0] == "\"":
                    return logic.DistinctObject(c0)
                else:
                    return logic.Constant(c0)

    def visit_quantified_formula(self, obj, **kwargs):
        if len(obj.children) == 1:
            return self.visit(obj.children[0])
        else:
            q = (
                logic.Quantifier.UNIVERSAL
                if obj.children[0] == "!"
                else logic.Quantifier.EXISTENTIAL
            )
            return logic.QuantifiedFormula(
                quantifier=q,
                variables=[self.visit(c, **kwargs) for c in obj.children[1:-1]],
                formula=self.visit(obj.children[-1], **kwargs),
            )

    def visit_unary_formula(self, obj, **kwargs):
        if len(obj.children) == 1:
            return self.visit(obj.children[0])
        else:
            return logic.UnaryFormula(
                connective=logic.UnaryConnective.NEGATION,
                formula=self.visit(obj.children[1], **kwargs),
            )

    @_recursive_binary(skip_connective=True)
    def visit_conjunction(self, obj, **kwargs):
        return logic.BinaryFormula(
            left=self.visit(obj.children[0], **kwargs),
            operator=logic.BinaryConnective.CONJUNCTION,
            right=self.visit(obj.children[1], **kwargs),
        )

    @_recursive_binary(skip_connective=True)
    def visit_disjunction(self, obj, **kwargs):
        return logic.BinaryFormula(
            left=self.visit(obj.children[0], **kwargs),
            operator=logic.BinaryConnective.DISJUNCTION,
            right=self.visit(obj.children[1], **kwargs),
        )

    @_recursive_binary(skip_connective=False)
    def visit_binary_formula(self, obj, **kwargs):
        return logic.BinaryFormula(
            left=self.visit(obj.children[0], **kwargs),
            operator=self.visit_binary_operator(obj.children[1], **kwargs),
            right=self.visit(obj.children[2], **kwargs),
        )

    def visit_type_binary_formula(self, obj, **kwargs):
        return self.visit_binary_formula(obj, **kwargs)

    def visit_logic_binary_formula(self, obj, **kwargs):
        return self.visit_binary_formula(obj, **kwargs)

    def visit_object_binary_formula(self, obj, **kwargs):
        if len(obj.children) > 1:
            kwargs["term_level"] = True
        return self.visit_binary_formula(obj, **kwargs)

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

    def visit_binary_operator(self, obj, **kwargs):
        return _BINARY_CONNECTIVE_MAP[obj]

    def visit_variable(self, obj, **kwargs):
        assert len(obj.children) == 1 and isinstance(obj.children[0], str)
        return logic.Variable(obj.children[0])

    def stream_formula_lines(self, lines: Iterable[str], **kwargs):
        buffer = ""
        for line in lines:
            if not line.startswith("%") and not line.startswith("\n"):
                buffer += line.strip()
                if buffer.endswith("."):
                    yield buffer
                    buffer = ""
        if buffer:
            raise Exception('Unprocessed input: """%s"""' % buffer)

    def visit_distinct_object(self, obj, **kwargs):
        assert len(obj.children) == 1 and isinstance(obj.children[0], str)
        return logic.DistinctObject(obj.children[0][1:-1])


if SUPPORTS_ANTLR:
    class TPTPAntlrParser(LogicParser, StringBasedParser):
        visitor = FOFFlatteningVisitor()

        def folder_processor(self, path, file_processor, *args, **kwargs):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not file == "README":
                        f = os.path.join(root, file)
                        yield file_processor(f, *args, **kwargs)

        def problemset_processor(self, *args, **kwargs):
            tptp_root = kwargs.get("tptp_root", settings.TPTP_ROOT)
            return self.folder_processor(
                os.path.join(tptp_root, "Problems"), self.problem_processor
            )

        def axiomsets_processor(self, *args, **kwargs):
            tptp_root = kwargs.get("tptp_root", settings.TPTP_ROOT)
            return self.folder_processor(
                os.path.join(tptp_root, "Axioms"), self.axiomset_processor
            )

        def axiomset_processor(self, path, *args, **kwargs):
            for item in self.load_expressions_from_file(path):
                yield self.formula_processor(item, *args, **kwargs)

        def formula_processor(self, formula, *args, orig=None, **kwargs):
            return formula

        def stream_formula_lines(self, lines: Iterable[str], **kwargs):
            buffer = ""
            for line in lines:
                if not line.startswith("%") and not line.startswith("\n"):
                    buffer += line.strip()
                    if buffer.endswith("."):
                        yield buffer
                        buffer = ""
            if buffer:
                raise Exception('Unprocessed input: """%s"""' % buffer)

        def load_single_from_string(self, string: str, *args, **kwargs):
            s = tptp_v7_0_0_0Parser(
                CommonTokenStream(tptp_v7_0_0_0Lexer(InputStream(string)))
            )
            return s.tptp_input()

        def load_expressions_from_file(
            self, path, *args, **kwargs
        ) -> Iterable[LogicElement]:
            with open(path) as infile:
                lines = infile.readlines()
                for line in self.load_many(lines):
                    yield self.parse(line)

        def parse(self, tree, *args, **kwargs):
            return self.visitor.visit(tree)

        def problem_processor(self, path, *args, load_imports=False, **kwargs):
            axioms = []
            imports = []
            conjectures = []
            for raw_line in self.load_expressions_from_file(path, *args, **kwargs):
                line = self.formula_processor(raw_line)
                if isinstance(line, logic.Import):
                    imports.append(line)
                elif isinstance(line, AnnotatedFormula):
                    if line.role in (
                        FormulaRole.CONJECTURE,
                        FormulaRole.NEGATED_CONJECTURE,
                    ):
                        conjectures.append(line)
                    else:
                        axioms.append(line)

            for im in imports:
                for imported_axiom in self.load_expressions_from_file(
                    os.path.join(settings.TPTP_ROOT, im.path), *args, **kwargs
                ):
                    axioms.append(imported_axiom)

            for conjecture in conjectures:
                yield Problem(premises=axioms, imports=imports, conjecture=conjecture)


class TPTPProblemParser(ProblemParser):
    logic_parser_cls = TPTPParser


class SimpleTPTPProofParser(ProofParser):
    def __init__(self):
        self._tptp_parser = TPTPParser()

    def parse(self, structure: str, *args, **kwargs):
        return LinearProof(
            steps=[
                self._create_proof_step(self._tptp_parser.parse(s))
                for s in self._tptp_parser.load_many(structure.split("\n"))
            ]
        )

    def _create_proof_step(self, e: LogicElement) -> ProofStep:
        if isinstance(e, AnnotatedFormula):
            if e.role == FormulaRole.AXIOM:
                return Axiom(formula=e.formula, name=e.name)
            elif e.role == FormulaRole.PLAIN:
                if isinstance(e.annotation, InferenceSource):
                    return Inference(
                        formula=e.formula, name=e.name, antecedents=e.annotation.parents
                    )
                elif isinstance(e.annotation, InternalSource):
                    return Introduction(
                        formula=e.formula,
                        name=e.name,
                        introduction_type=e.annotation.intro_type,
                    )
            raise ParserException(e)
        else:
            raise ParserException(e)


def get_all_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file == "README":
                yield os.path.join(root, file)


def all_problems(processor):
    for f in get_all_files(os.path.join(settings.TPTP_ROOT, "Problems")):
        print(f)
        for problem in processor.problem_processor(f):
            print("done")


def all_solution(path, system=""):
    path = os.path.join(path, "Problems")
    files = get_all_files(path)
    for file in files:
        domain, problem = os.path.normpath(file).split(os.sep)[-2:]
        response = requests.get(
            "http://www.tptp.org/cgi-bin/SeeTPTP?Category=Solutions"
            "&Domain={domain}"
            "&File={problem}"
            "&System=Vampire---4.3.THM-Ref.s".format(
                domain=domain, problem=problem[:-2]
            )
        )
        print(response)
