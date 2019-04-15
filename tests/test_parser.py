import pytest as pt

from gavel.language.tptp.processor import Processor, StorageProcessor, all_axioms
from gavel.language.base.compiler import Compiler
from gavel.io.connection import with_session
from gavel.settings import TPTP_ROOT
from os.path import join

import cProfile, pstats

class TestProcessor(Processor):
    compiler = Compiler()

    def syntax_tree_processor(self, tree, *args, **kwargs):
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
def test_single_line():
    processor = TestProcessor()

    for _ in processor.load_expressions_from_file('single_line_thf.txt'):
        pass

class TestAxioms:
    def test_MATH001_0(self):
        single_axiom('MAT001^0.ax')


class TestProblems:
    def test_NUN030_1(self):
        single_problem('NUN/NUN030^1.p')

    def test_ALG001_1(self):
        single_problem('ALG/ALG001-1.p')


#@with_session
#def test_single_problem(session):
#    processor = StorageProcessor()
#    for problem in processor.problem_processor(join(TPTP_ROOT,'Problems/ALG/ALG001-1.p'), session=session):
#        problem.create_problem_file()


if __name__ == "__main__":
    pass
    #test_single_axiom()
    #TestProblems()
    #test_single_problem()
    #test_axiom_parser()
