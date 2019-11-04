import cProfile
import pstats
import unittest
from os.path import join

import pytest

import gavel.dialects.db.structures as fol_db
from gavel.config.settings import TPTP_ROOT
from gavel.dialects.db.connection import with_session
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import TPTPParser


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

axioms = ["GRP001-0.ax"]

problems = ["ALG/ALG001-1.p", "NUN/NUN030^1.p"]


class DBTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        fol_db.create_tables()

    @classmethod
    def teardown_class(cls):
        fol_db.drop_tables()


