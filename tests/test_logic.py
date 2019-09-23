import unittest

from gavel.dialects.tptp.antlr4 import tptp_v7_0_0_0Parser
from gavel.dialects.tptp.parser import TPTPParser


class TestFOL(unittest.TestCase):
    def test_symbols(self):
        processor = TPTPParser()
        result = list(
            processor.load_expressions_from_file("tests/files/single_line_fof.txt")
        )
        self.assertEqual(len(result), 1, "Single line was not parsed as single line")
        line = result[0]
        self.assertSetEqual(set(line.symbols()), {"ismeet", "leq"})
