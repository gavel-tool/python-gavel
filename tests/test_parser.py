import pytest as pt

from gavel.language.tptp.build import Processor
from gavel.language.base.compiler import Compiler
from gavel.language.tptp.build import all_axioms


class TestProcessor(Processor):
    compiler = Compiler()

    def syntax_tree_processor(self, tree, visitor, *args, **kwargs):
        original = tree.getText()
        internal = visitor.visit(tree)
        if internal.logic != "thf":
            reconstructed = self.compiler.visit(internal)
            assert original.replace("(", "").replace(")", "") == reconstructed.replace(
                "(", ""
            ).replace(")", ""), (original, reconstructed)


def test_axiom_parser():
    for axiom_set in all_axioms(TestProcessor()):
        for line in axiom_set:
            pass


def test_thf_axiom():
    processor = TestProcessor()
    for line in processor.axiomset_processor("Axioms/DAT004=0.ax"):
        pass


if __name__ == "__main__":
    # test_thf_axiom()
    test_axiom_parser()
