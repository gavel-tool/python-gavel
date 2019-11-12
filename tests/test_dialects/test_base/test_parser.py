import unittest
from itertools import chain

from gavel.dialects.base.parser import LogicElement, Problem
from gavel.dialects.base.parser import LogicParser, ProblemParser
from gavel.logic.problem import AnnotatedFormula, FormulaRole
from gavel.logic import logic
class TestLogicParser(unittest.TestCase):
    _parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        super(TestLogicParser, self).__init__(*args, **kwargs)
        self.parser = self._parser_cls()

    def assertObjectEqual(self, result, expected):
        self.assertTrue(isinstance(result, type(expected)) or isinstance(expected, type(result)), "Types do not math: (expected: %s, got: %s)" % (type(expected), type(result)))
        if isinstance(result, LogicElement) or isinstance(result, AnnotatedFormula) or isinstance(result, Problem):
            for n in chain(result.__dict__.keys(), expected.__dict__.keys()):
                self.assertObjectEqual(getattr(result, n), getattr(expected, n))
        elif isinstance(result, list):
            assert len(result) == len(expected)
            for po1, po2 in zip(result, expected):
                self.assertObjectEqual(po1, po2)
        elif isinstance(result, str):
            self.assertEqual(str(result), str(expected))
        else:
            self.assertEqual(result, expected)

    def check_parser(self, parser_input, expected):
        r = self.parser.parse_single_from_string(parser_input)
        self.assertObjectEqual(r, expected)

class TestProblemParser(TestLogicParser):
    _parser_cls = ProblemParser

    def check_parser(self, parser_input, expected):
        r = list(self.parser.parse(parser_input))
        self.assertObjectEqual(r, expected)

def check_wrapper(logic_name="fof",name="name"):
    def outer(f):
        def inner(self: TestLogicParser):
            formula, expected_formula = f(self)
            string = "{logic}({name},{role},{formula}).".format(
                logic=logic_name,
                name=name,
                role="plain",
                formula=formula
            )
            result = self.parser.parse_single_from_string(string)
            expected = AnnotatedFormula(
                logic=logic_name,
                name=name,
                role=FormulaRole.PLAIN,
                formula=expected_formula
            )
            self.assertObjectEqual(result, expected)
        return inner
    return outer
