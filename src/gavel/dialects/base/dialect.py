from typing import Iterable

from gavel.dialects.base.compiler import Compiler
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.base.parser import ProofParser
from gavel.logic.problem import Problem
from gavel.logic.proof import Proof


class Dialect:
    _problem_parser_cls = ProblemParser
    _compiler_cls = Compiler
    _proof_parser_cls = ProofParser

    def compile(self, obj: Problem, *args, **kwargs):
        c = self._compiler_cls()
        return c.visit(obj, *args, **kwargs)

    def compile_problem(self, obj: Problem, *args, **kwargs):
        c = self._compiler_cls()
        return c.visit_problem(obj, *args, **kwargs)

    def parse_problem(self, string: str, *args, **kwargs) -> Problem:
        p = self._problem_parser_cls()
        return p.parse(string, *args, **kwargs)

    def parse_many_expressions(
        self, strings: Iterable[str], *args, **kwargs
    ) -> Iterable:
        p = self._problem_parser_cls.logic_parser_cls()
        return p.load_many(strings, *args, **kwargs)

    def parse_expression(self, string: str, *args, **kwargs) -> Problem:
        p = self._problem_parser_cls.logic_parser_cls()
        return p.parse(string, *args, **kwargs)

    def parse_expression_from_string(self, string: str, *args, **kwargs) -> Problem:
        p = self._problem_parser_cls.logic_parser_cls()
        return p.parse_from_string(string, *args, **kwargs)

    def compile_and_render(self, obj: Problem, *args, **kwargs):
        c = self._compiler_cls()
        compiled = c.visit(obj, *args, **kwargs)
        return r.render(compiled, *args, **kwargs)

    def parse_proof(self, prover_output) -> Proof:
        p = self._proof_parser_cls()
        return p.parse(prover_output)
