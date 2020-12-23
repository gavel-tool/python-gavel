from gavel.dialects.tptp.parser import (
    TPTPParser,
    TPTPProblemParser,
    SimpleTPTPProofParser,
)
from gavel.logic import logic
from gavel.logic import problem
from gavel.logic import solution
from gavel.logic import sources

from ..test_base.test_parser import (
    TestLogicParser,
    check_wrapper,
    TestProblemParser,
    TestProofParser,
)


class TestTPTPProblemParser(TestProblemParser):
    _parser_cls = TPTPParser
