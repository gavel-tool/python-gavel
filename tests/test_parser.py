from gavel.dialects.tptp.tptpparser import TPTPParser, StorageProcessor
from gavel.dialects.tptp.compiler import Compiler
from gavel.dialects.db.connection import with_session
from gavel.settings import TPTP_ROOT
from os.path import join

import cProfile, pstats

import unittest

class TestProcessor(TPTPParser):
    compiler = Compiler()

    def parse(self, tree, *args, **kwargs):
        original = tree.getText()
        internal = self.visitor.visit(tree)
        if internal.logic != "thf":
            reconstructed = self.compiler.visit(internal)
            assert original.replace("(", "").replace(")", "") == reconstructed.replace(
                "(", ""
            ).replace(")", ""), (original, reconstructed)
            print(reconstructed)
        return internal


#def test_single_axiom():
#    processor = TestProcessor()
#    for line in processor.axiomset_processor(join(TPTP_ROOT,"Axioms/CSR003+2.ax")):
#        pass

axioms = [
    'GRP001-0.ax'
]

problems = [
    'ALG/ALG001-1.p',
    'NUN/NUN030^1.p'
]



@with_session
def single_problem(problem,session):
    processor = StorageProcessor()
    for problem in processor.problem_processor(join(TPTP_ROOT,join('Problems', problem)), session=session):
        problem.create_problem_file()

def single_axiom(axiom):
    p = cProfile.Profile()
    p.enable()
    processor = TestProcessor()
    for _ in processor.axiomset_processor(join(TPTP_ROOT, join('Axioms', axiom))):
        pass
    p.disable()
    p.print_stats(sort=pstats.SortKey.TIME)

class TestParser(unittest.TestCase):
    def test_single_line(self):
        processor = TestProcessor()

        for _ in processor.load_expressions_from_file('tests/files/single_line_thf.txt'):
            pass

class TestAxiomsCNF(unittest.TestCase):
    def test_RNG001_0(self):
        single_axiom('RNG001-0.ax')


class TestAxiomsFOF(unittest.TestCase):
    def test_AGT001_0(self):
        single_axiom('AGT001+0.ax')


class TestProblems:
    def test_NUN030_1(self):
        single_problem('NUN/NUN030^1.p')

    def test_ALG001_1(self):
        single_problem('ALG/ALG001-1.p')
