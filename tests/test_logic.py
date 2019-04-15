from gavel.language.tptp.parser import tptp_v7_0_0_0Parser
from gavel.language.tptp.processor import Processor
import unittest


class TestFOL(unittest.TestCase):
    def test_symbols(self):
        processor = Processor()
        result = list(processor.load_expressions_from_file('single_line_fof.txt'))
        self.assertEqual(len(result), 1, "Single line was not parsed as single line")
        line, _ = result[0]
        self.assertSetEqual(set(line.symbols()), {'X0', 'X1', 'X2', 'X3', 'ismeet', 'leq'})


