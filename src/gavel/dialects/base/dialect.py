from typing import Iterable

from gavel.dialects.base.compiler import Compiler
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.base.parser import ProofParser
from gavel.logic.problem import Problem
from gavel.logic.proof import Proof


class Dialect:
    _parser_cls = ProblemParser
    _compiler_cls = Compiler

    def compile(self, obj: Problem, *args, **kwargs):
        c = self._compiler_cls()
        return c.visit(obj, *args, **kwargs)



    def parse_many_expressions(
        self, strings: Iterable[str], *args, **kwargs
    ) -> Iterable:
        p = self._parser_cls.logic_parser_cls()
        return p.load_many(strings, *args, **kwargs)

    def parse_expression(self, string: str, *args, **kwargs) -> Problem:
        p = self._parser_cls.logic_parser_cls()
        return p.parse(string, *args, **kwargs)

    def parse_expression_from_string(self, string: str, *args, **kwargs) -> Problem:
        p = self._parser_cls.logic_parser_cls()
        return p.parse_single_from_string(string, *args, **kwargs)


class IdentityDialect(Dialect):

    def compile_problem(self, obj: Problem, *args, **kwargs):
        return obj

    def parse_proof(self, prover_output) -> Proof:
        return prover_output
