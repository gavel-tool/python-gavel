import gavel.dialects.db.structures as db
import gavel.settings as settings
from gavel.dialects.base.parser import LogicParser
from gavel.dialects.base.parser import Parseable
from gavel.dialects.base.parser import Parser
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.db.connection import get_or_create
from gavel.dialects.db.connection import get_or_None
from gavel.dialects.db.connection import with_session
from gavel.logic import fol
from gavel.logic.base import LogicElement
from gavel.logic.base import Problem
from gavel.logic.base import Sentence
from gavel.logic.fol import FormulaRole
from gavel.settings import TPTP_ROOT


class DBProblemParser(ProblemParser):
    logic_parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        self.logic_parser = LogicParser(*args, **kwargs)

    def parse(self, structure: Parseable, *args, **kwargs):
        premises = []
        conjectures = []
        for s in self.logic_parser.parse(structure):
            if isinstance(s, Sentence):
                if s.is_conjecture():
                    conjectures.append(s)
                else:
                    premises.append(s)
        for c in conjectures:
            yield Problem(premises, c)
