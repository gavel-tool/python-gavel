import unittest
from itertools import chain

from gavel.dialects.base.parser import LogicElement
from gavel.dialects.base.parser import LogicParser
from gavel.logic.problem import AnnotatedFormula


class TestLogicParser(unittest.TestCase):
    _parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        super(TestLogicParser, self).__init__(*args, **kwargs)
        self.parser = self._parser_cls()

    def assertObjectEqual(self, o1, o2):
        self.assertEqual(type(o1), type(o2))
        if isinstance(o1, LogicElement) or isinstance(o1, AnnotatedFormula):
            for n in chain(o1.__dict__.keys(), o2.__dict__.keys()):
                self.assertObjectEqual(getattr(o1, n), getattr(o2, n))
        elif isinstance(o1, list):
            for po1, po2 in zip(o1, o2):
                self.assertObjectEqual(po1, po2)
        else:
            self.assertEqual(o1, o2)

    def check_parser(self, parser_input, expected):
        r = self.parser.parse_single_from_string(parser_input)
        self.assertObjectEqual(r, expected)
