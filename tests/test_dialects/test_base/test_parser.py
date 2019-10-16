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

    def assertObjectEqual(self, result, expected):
        self.assertTrue(isinstance(result, type(expected)) or isinstance(expected, type(result)), "Types do not math: (expected: %s, got: %s)" % (type(expected), type(result)))
        if isinstance(result, LogicElement) or isinstance(result, AnnotatedFormula):
            for n in chain(result.__dict__.keys(), expected.__dict__.keys()):
                self.assertObjectEqual(getattr(result, n), getattr(expected, n))
        elif isinstance(result, list):
            for po1, po2 in zip(result, expected):
                self.assertObjectEqual(po1, po2)
        else:
            self.assertEqual(result, expected)

    def check_parser(self, parser_input, expected):
        r = self.parser.parse_single_from_string(parser_input)
        self.assertObjectEqual(r, expected)
