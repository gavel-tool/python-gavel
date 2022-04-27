import os
import re
import sys
from bs4 import BeautifulSoup
from typing import Iterable
import requests
import multiprocessing as mp
from itertools import chain
try:
    from antlr4 import CommonTokenStream
    from antlr4 import InputStream
except:
    SUPPORTS_ANTLR = False
else:
    SUPPORTS_ANTLR = True

from gavel.config import settings as settings
from gavel.dialects.base.parser import LogicParser, Target, StringBasedParser
from gavel.dialects.base.parser import ParserException
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.base.parser import ProofParser
from gavel.logic import logic, sources
from gavel.logic.logic import LogicElement
from gavel.logic import problem as tptp_problem
from gavel.logic.problem import AnnotatedFormula
from gavel.logic.solution import LinearProof
from gavel.logic.solution import ProofStep
from gavel.logic import status

if SUPPORTS_ANTLR:
    pass

from lark import Lark, Tree, Transformer

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


class TPTPTransformer(Transformer):

    def transform(self, tree):
        pass

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

    def visit_file_source(self, obj):
        file_name = self.visit(obj.children[0]).replace("'", "")
        return sources.FileSource(file_name, *map(self.visit, obj.children[1:]))

    def visit_inference_source(self, obj):
        return sources.InferenceSource(*map(self.visit, obj.children))

    def visit_internal_source(self, obj):
        return sources.InternalSource(*map(self.visit, obj.children))

    def visit_generic_annotation(self, obj):
        return sources.GenericSource(
            *map(lambda x: self.visit(x).strip(), obj.children)
        )

    def visit_sources(self, obj, **kwargs):
        return [self.visit(s) for s in obj.children]

    def visit_annotation(self, obj, **kwargs):
        return self.visit(obj.children[0], **kwargs)

    def visit_start(self, obj, **kwargs):
        return [self.visit(c) for c in obj.children]

    def visit_include(self, obj):
        if len(obj.children) > 1:
            filter = [s for s in obj.children[1:]]
        return tptp_problem.Import(os.path.join(settings.TPTP_ROOT, str(obj.children[0])))

    def visit_tptp_line(self, obj, **kwargs):
        return self.visit(obj.children[0], **kwargs)

    def visit_annotated_formula(self, obj, **kwargs):
        annotations = dict()
        if len(obj.children) > 4:
            annotations["annotation"] = self.visit(obj.children[4])
        return tptp_problem.AnnotatedFormula(
            logic=obj.children[0],
            name=obj.children[1],
            role=self._ROLE_MAP[obj.children[2]],
            formula=self.visit(obj.children[3], **kwargs),
            **annotations
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
                p = self._DEFINED_PREDICATE_MAP.get(c0, c0) if is_defined else c0
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
                    return logic.DefinedConstant(logic.PredefinedConstant.VERUM)
                elif c0 == "$false":
                    return logic.DefinedConstant(logic.PredefinedConstant.FALSUM)
                else:
                    return logic.DefinedConstant(self.visit(c0))
            else:
                if c0[0] == '"':
                    return logic.DistinctObject(c0)
                else:
                    return logic.Constant(c0)

    def visit_decimal_number(self, obj, **kwargs):
        return logic.DefinedConstant(obj)

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
        "axiom": tptp_problem.FormulaRole.AXIOM,
        "hypothesis": tptp_problem.FormulaRole.HYPOTHESIS,
        "definition": tptp_problem.FormulaRole.DEFINITION,
        "assumption": tptp_problem.FormulaRole.ASSUMPTION,
        "lemma": tptp_problem.FormulaRole.LEMMA,
        "theorem": tptp_problem.FormulaRole.THEOREM,
        "corollary": tptp_problem.FormulaRole.COROLLARY,
        "conjecture": tptp_problem.FormulaRole.CONJECTURE,
        "negated_conjecture": tptp_problem.FormulaRole.NEGATED_CONJECTURE,
        "plain": tptp_problem.FormulaRole.PLAIN,
        "type": tptp_problem.FormulaRole.TYPE,
        "fi_domain": tptp_problem.FormulaRole.FINITE_INTERPRETATION_DOMAIN,
        "fi_functors": tptp_problem.FormulaRole.FINITE_INTERPRETATION_FUNCTORS,
        "fi_predicates": tptp_problem.FormulaRole.FINITE_INTERPRETATION_PREDICATES,
        "unknown": tptp_problem.FormulaRole.UNKNOWN,
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

    def visit_typed_variable(self, obj, **kwargs):
        return logic.TypedVariable(self.visit(obj.children[0]), self.visit(obj.children[1]))

    def stream_items(self, lines: Iterable[str], **kwargs):
        return ["\n".join(lines)]

    def visit_distinct_object(self, obj, **kwargs):
        assert len(obj.children) == 1 and isinstance(obj.children[0], str)
        return logic.DistinctObject(obj.children[0][1:-1])

    def start(self, obj):
        for c in obj:
            yield self.visit(c)

lark_grammar = Lark.open(
    os.path.join(os.path.dirname(__file__), "tptp.lark"),
    start=["start"],
    parser="lalr",
    transformer=TPTPTransformer())


def do(string):
    try:
        return list(lark_grammar.parse(string))
    except Exception as e:
        raise Exception(str(e))


class TPTPParser(LogicParser, StringBasedParser):
    def __init__(self):
        sys.setrecursionlimit(100000)
        self.visitor = TPTPTransformer()
        part = r"^(\w+\(([\sA-z0-9_,!?[:()='\"&|$\/\]]|(?<!\)).)+\)\.)"
        full = f"(%[^\n]*\s*(\s|$))|{part}\s*"
        self._re_full = re.compile(f"({full})+", flags=re.X)
        self._re_part = re.compile(part)

    def is_valid(self, inp: str) -> bool:
        pass

    def stream_lines(self, string):
        buff = ""
        newline = True
        comment = False
        quoted = False
        for x in string:
            if not quoted and not comment and x == "." and buff[-1] == ")":
                yield buff + "."
                buff = ""
            else:
                if newline and x == "%":
                    comment = True
                else:
                    if x == "\n":
                        comment = False
                        newline = True
                    elif newline:
                        newline = False
                    elif not comment:
                        if quoted and x == quoted and buff[-1] != "\\":
                            quoted = False
                        elif x == "'" or x =='"':
                            quoted = x
                buff += x
        yield buff

    def parse(self, structure: str, *args, **kwargs) -> Target:
        inputs = self.stream_lines(structure)
        with mp.get_context("spawn").Pool() as pool:
            return list(chain(*pool.imap(do, inputs)))


class TPTPProblemParser(ProblemParser, StringBasedParser):
    logic_parser_cls = TPTPParser


class SimpleTPTPProofParser(ProofParser):
    def __init__(self):
        self._tptp_parser = TPTPParser()

    def parse(self, structure: str, *args, **kwargs):
        szs_status = re.search(r"SZS status (\w+)", structure)
        if szs_status:
            try:
                szs_status = status.get_status(szs_status.groups()[0])()
            except:
                print("Warning: Could not process proof status:", szs_status)
                szs_status = None
        if not szs_status:
            szs_status = status.StatusUnknown()
        return LinearProof(
            steps=[
                self._create_proof_step(s) for s in self._tptp_parser.parse(structure)
            ],
            status=szs_status
        )

    def _create_proof_step(self, e: LogicElement) -> ProofStep:
        if isinstance(e, AnnotatedFormula):
            return e
        else:
            raise ParserException(e)


def get_all_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file == "README":
                yield os.path.join(root, file)


def all_problems(processor: StringBasedParser):
    for f in get_all_files(os.path.join(settings.TPTP_ROOT, "Problems")):
        with open(f, "r") as infile:
            for problem in processor.parse(infile.readlines()):
                yield f, problem


def _extract_pre(strings):
    capture = False
    for line in strings:
        if capture:
            if "</pre>" in line:
                capture = False
            else:
                yield line
        if "<pre>" in line:
            capture = True


def all_available_problem_names(path, system=""):
    path = os.path.join(path, "Problems")
    files = get_all_files(path)
    for file in files:
        yield os.path.normpath(file).split(os.sep)[-2:]


def _load_solution(domain, name):
    response = requests.get(
        "http://www.tptp.org/cgi-bin/SeeTPTP?Category=Solutions"
        "&Domain={domain}"
        "&File={problem}"
        "&System=E---2.5".format(domain=domain, problem=name)
    )
    raw_string = response.content.decode("utf-8")
    return "\n".join(_extract_pre(raw_string.split("\n")))


def parse_solution(prover_output):
    if prover_output:
        soup = BeautifulSoup(
            prover_output
        )  # "".join(map(h.handle, prover_output.split("\n")))
        szs_status = re.search(r"SZS status (\w+)", soup.get_text())
        if szs_status:
            szs_status = status.get_status(szs_status.groups()[0])
        else:
            szs_status = status.StatusUnknown
        if issubclass(szs_status, status.StatusSuccess):
            parser = SimpleTPTPProofParser()
            solution = parser.parse(soup.get_text())
            return solution


if __name__=="__main__":
    pass
