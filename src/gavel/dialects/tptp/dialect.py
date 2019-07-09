from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import TPTPProblemParser
from gavel.dialects.base.dialect import Dialect
from gavel.logic.base import Problem


class TPTPDialect(Dialect):
    _problem_parser_cls = TPTPProblemParser
    _compiler_cls = TPTPCompiler
