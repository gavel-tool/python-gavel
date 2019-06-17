from gavel.dialects.base.compiler import Compiler
from gavel.dialects.base.parser import ProblemParser
from gavel.logic.base import Problem

class Dialect:
    _problem_parser = ProblemParser
    _compiler = Compiler

    def compile(self, obj: Problem, *args, **kwargs):
        c = self._compiler()
        return c.visit(obj, *args, **kwargs)

    def parse(self, string: str, *args, **kwargs) -> Problem:
        p = self._problem_parser()
        return p.parse(string, *args, **kwargs)

    def compile_and_render(self, obj: Problem, *args, **kwargs):
        c = self._compiler()
        compiled = c.visit(obj, *args, **kwargs)
        return r.render(compiled, *args, **kwargs)
