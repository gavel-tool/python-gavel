from typing import Iterable

from gavel.dialects.base.compiler import Compiler
from gavel.dialects.base.parser import Parser
from gavel.logic.problem import Problem
from gavel.logic.solution import Proof

_DIALECT_REGISTRY = {}


class Dialect:
    _parser_cls = Parser
    _compiler_cls = Compiler

    def __init__(
        self,
        parser_args=None,
        parser_kwargs=None,
        compiler_args=None,
        compiler_kwargs=None,
    ):
        if compiler_args is None:
            compiler_args = []
        if compiler_kwargs is None:
            compiler_kwargs = dict()
        if parser_args is None:
            parser_args = []
        if parser_kwargs is None:
            parser_kwargs = dict()
        self._parser = self._parser_cls(*parser_args, **parser_kwargs)
        self._compiler = self._compiler_cls(*compiler_args, **compiler_kwargs)

    def __init_subclass__(cls, **kwargs):
        _DIALECT_REGISTRY[cls._identifier()] = cls

    def compile(self, obj, *args, **kwargs):
        return self._compiler.visit(obj, *args, **kwargs)

    def parse(self, obj, *args, **kwargs):
        return self._parser.parse(obj, *args, **kwargs)

    @classmethod
    def _identifier(cls) -> str:
        raise NotImplementedError


class IdentityDialect(Dialect):
    def compile(self, obj: Problem, *args, **kwargs):
        return obj

    def parse(self, obj, *args, **kwargs):
        return obj

    @classmethod
    def _identifier(cls) -> str:
        return "id"


def get_dialect(identifier) -> Dialect:
    return _DIALECT_REGISTRY[identifier]
