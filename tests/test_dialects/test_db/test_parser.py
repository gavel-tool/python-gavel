import cProfile
import pstats
import unittest
from os.path import join
import pytest

from gavel.dialects.db.connection import with_session
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import StorageProcessor
from gavel.dialects.tptp.parser import TPTPParser
from gavel.config.settings import TPTP_ROOT
import gavel.dialects.db.structures as fol_db


class TestProcessor(TPTPParser):
    compiler = TPTPCompiler()

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


# def test_single_axiom():
#    processor = TestProcessor()
#    for line in processor.axiomset_processor(join(TPTP_ROOT,"Axioms/CSR003+2.ax")):
#        pass

axioms = ["GRP001-0.ax"]

problems = ["ALG/ALG001-1.p", "NUN/NUN030^1.p"]


class DBTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        fol_db.create_tables()

    @classmethod
    def teardown_class(cls):
        fol_db.drop_tables()

@with_session
def single_problem(problem, session):
    processor = StorageProcessor()
    for problem in processor.problem_processor(
        join(TPTP_ROOT, join("Problems", problem)), session=session
    ):
        p = problem


def single_axiom(axiom):
    processor = TestProcessor()
    for _ in processor.axiomset_processor(join(TPTP_ROOT, join("Axioms", axiom))):
        pass


class TestParser(unittest.TestCase):
    def test_single_line(self):
        processor = TestProcessor()

        for _ in processor.load_expressions_from_file(
            "tests/files/single_line_thf.txt"
        ):
            pass

