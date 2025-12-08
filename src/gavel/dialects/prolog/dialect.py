from gavel.dialects.base.dialect import Dialect
from gavel.dialects.prolog.parser import PrologParser


class PrologDialect(Dialect):
    _parser_cls = PrologParser
    _compiler_cls = None

    @classmethod
    def _identifier(cls) -> str:
        return "prolog"