from unittest import TestCase

import pytest

from gavel.dialects.base.compiler import Compiler


class TestCompiler(TestCase):
    compiler = Compiler

    @pytest.mark.skip
    def assert_compiler(self, structure, expected):
        c = self.compiler()
        self.assertEqual(c.visit(structure), expected)
