from gavel.dialects.base.dialect import Dialect
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import SimpleTPTPProofParser
from gavel.dialects.tptp.parser import TPTPProblemParser
from gavel.logic.problem import Problem


class TPTPProblemDialect(Dialect):
    _parser_cls = TPTPProblemParser
    _compiler_cls = TPTPCompiler

    @classmethod
    def _identifier(self):
        return "tptp"


# For legacy code
TPTPDialect = TPTPProblemDialect


class TPTPProofDialect(Dialect):
    _parser_cls = SimpleTPTPProofParser
    _compiler_cls = TPTPCompiler

    @classmethod
    def _identifier(cls) -> str:
        return "tptp-proof"
