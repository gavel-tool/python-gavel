import pytest as pt

from chisel.language.tptp.build import Processor
from chisel.language.base.compiler import Compiler
from chisel.language.tptp.run import all_axioms


class TestProcessor(Processor):
    compiler = Compiler()

    def syntax_tree_processor(self, tree, visitor, *args, **kwargs):
        original = tree.getText()
        internal = visitor.visit(tree)
        if internal.logic in ('tfo', 'fof', 'cnf'):
            reconstructed = self.compiler.visit(internal)
            assert original.replace('(','').replace(')','') == reconstructed.replace('(','').replace(')',''), (original, reconstructed)
        else:
            print(internal.logic)

def test_axiom_parser():
    for axiom_set in all_axioms(TestProcessor()):
        for line in axiom_set:
            pass


def test_thf_axiom():
    processor = TestProcessor()
    for line in processor.axiomset_processor('Axioms/PHI001^0.ax'):
        pass


if __name__=='__main__':
    #test_thf_axiom()
    test_axiom_parser()
