import unittest
from itertools import chain

from gavel.dialects.base.parser import LogicElement
from gavel.dialects.base.parser import LogicParser, StringBasedParser
from gavel.dialects.base.compiler import Compiler
from gavel.logic.problem import AnnotatedFormula


class TestLogicRoundtrip(unittest.TestCase):
    _parser_cls = StringBasedParser
    _compiler_cls = Compiler

    def __init__(self, *args, **kwargs):
        super(TestLogicRoundtrip, self).__init__(*args, **kwargs)
        self.parser = self._parser_cls()
        self.compiler = self._compiler_cls()

    def check_roundtrip(self, expected, ignore_space=False):
        result = self.compiler.visit(self.parser.parse_single_from_string(expected))
        for x in [" ", "\n"]:
            expected = expected.replace(x, "")
            result = result.replace(x, "")
        self.assertEqual(result, expected)

    def assertObjectEqual(self, result, expected):
        self.assertTrue(
            isinstance(result, type(expected)) or isinstance(expected, type(result)),
            "Types do not math: (expected: %s, got: %s)"
            % (type(expected), type(result)),
        )
        if isinstance(result, LogicElement) or isinstance(result, AnnotatedFormula):
            for n in chain(result.__dict__.keys(), expected.__dict__.keys()):
                self.assertObjectEqual(getattr(result, n), getattr(expected, n))
        elif isinstance(result, list):
            for po1, po2 in zip(result, expected):
                self.assertObjectEqual(po1, po2)
        else:
            self.assertEqual(result, expected)


def check_roundtrip_wrapper(logic="fof", name="name", role="plain"):
    def outer(f):
        def inner(self: TestLogicRoundtrip):
            formula = f(self)
            string = "{logic}({name},{role},{formula})".format(
                logic=logic, name=name, role=role, formula=formula
            )
            self.check_roundtrip(string)

        return inner

    return outer
