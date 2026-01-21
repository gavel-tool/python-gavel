from gavel.dialects.base.dialect import Dialect
from gavel.dialects.logic_programs.parser import LogicProgramParser


class LogicProgramDialect(Dialect):
    _parser_cls = LogicProgramParser
    _compiler_cls = None

    @classmethod
    def _identifier(cls) -> str:
        return "logic_programs"