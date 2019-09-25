import os
import pickle as pkl
import re
import sys
from typing import Iterable

import requests
from antlr4 import CommonTokenStream
from antlr4 import InputStream

import gavel.config.settings as settings
import gavel.dialects.db.structures as db
from gavel.config import settings as settings
from gavel.dialects.base.parser import LogicParser
from gavel.dialects.base.parser import ParserException
from gavel.dialects.base.parser import ProblemParser
from gavel.dialects.base.parser import ProofParser
from gavel.dialects.db.compiler import DBCompiler
from gavel.dialects.db.connection import get_or_create
from gavel.dialects.db.connection import get_or_None
from gavel.dialects.db.connection import with_session
from gavel.dialects.tptp.sources import InferenceSource
from gavel.dialects.tptp.sources import Input
from gavel.dialects.tptp.sources import InternalSource
from gavel.logic import logic
from gavel.logic import problem
from gavel.logic.logic import LogicElement
from gavel.logic.problem import AnnotatedFormula
from gavel.logic.problem import FormulaRole
from gavel.logic.problem import Problem
from gavel.logic.proof import Axiom
from gavel.logic.proof import Inference
from gavel.logic.proof import Introduction
from gavel.logic.proof import LinearProof
from gavel.logic.proof import ProofStep

from .antlr4.flattening import FOFFlatteningVisitor
from .antlr4.tptp_v7_0_0_0Lexer import tptp_v7_0_0_0Lexer
from .antlr4.tptp_v7_0_0_0Parser import tptp_v7_0_0_0Parser

sys.setrecursionlimit(10000)

form_expression = re.compile(r"^(?!%|\n)(?P<logic>[^(]*)\([^.]*\)\.\S*$")


class TPTPParser(LogicParser):
    visitor = FOFFlatteningVisitor()

    def folder_processor(self, path, file_processor, *args, **kwargs):
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file == "README":
                    f = os.path.join(root, file)
                    yield file_processor(f, *args, **kwargs)

    def problemset_processor(self, *args, **kwargs):
        tptp_root = kwargs.get("tptp_root", settings.TPTP_ROOT)
        return self.folder_processor(
            os.path.join(tptp_root, "Problems"), self.problem_processor
        )

    def axiomsets_processor(self, *args, **kwargs):
        tptp_root = kwargs.get("tptp_root", settings.TPTP_ROOT)
        return self.folder_processor(
            os.path.join(tptp_root, "Axioms"), self.axiomset_processor
        )

    def axiomset_processor(self, path, *args, **kwargs):
        for item in self.load_expressions_from_file(path):
            yield self.formula_processor(item, *args, **kwargs)

    def formula_processor(self, formula, *args, orig=None, **kwargs):
        return formula

    def stream_formula_lines(self, lines: Iterable[str], **kwargs):
        buffer = ""
        for line in lines:
            if not line.startswith("%") and not line.startswith("\n"):
                buffer += line.strip()
                if buffer.endswith("."):
                    yield buffer
                    buffer = ""
        if buffer:
            raise Exception('Unprocessed input: """%s"""' % buffer)

    def load_string(self, string: str, *args, **kwargs):
        return tptp_v7_0_0_0Parser(
            CommonTokenStream(tptp_v7_0_0_0Lexer(InputStream(string)))
        ).tptp_input()

    def load_expressions_from_file(
        self, path, *args, **kwargs
    ) -> Iterable[LogicElement]:
        with open(path) as infile:
            lines = infile.readlines()
            return self.load_many(lines)

    def load_many(
        self, lines: Iterable[str], *args, **kwargs
    ) -> Iterable[LogicElement]:
        # pool = mp.Pool(mp.cpu_count() - 1)
        for tree in map(
            self.parse_from_string, self.stream_formula_lines(lines, **kwargs)
        ):
            yield tree
        # pool.close()

    def parse(self, tree, *args, **kwargs) -> LogicElement:
        return self.visitor.visit(tree)

    def file_processor(self, path, *args, **kwargs):
        return self.load_expressions_from_file(path, *args, **kwargs)

    def problem_processor(self, path, *args, load_imports=False, **kwargs):
        axioms = []
        imports = []
        conjectures = []
        for raw_line in self.load_expressions_from_file(path, *args, **kwargs):
            line = self.formula_processor(raw_line)
            if isinstance(line, logic.Import):
                imports.append(line)
            elif isinstance(line, AnnotatedFormula):
                if line.role in (
                    FormulaRole.CONJECTURE,
                    FormulaRole.NEGATED_CONJECTURE,
                ):
                    conjectures.append(line)
                else:
                    axioms.append(line)

        for im in imports:
            for imported_axiom in self.file_processor(
                os.path.join(settings.TPTP_ROOT, im.path), *args, **kwargs
            ):
                axioms.append(imported_axiom)

        for conjecture in conjectures:
            yield Problem(premises=axioms, imports=imports, conjecture=conjecture)


class StorageProcessor(TPTPParser):
    def __init__(self):
        self.compiler = DBCompiler()

    @with_session
    def problem_processor(self, path, *args, **kwargs):
        session = kwargs.get("session")
        source, s_created = get_or_create(session, db.Source, path=path)
        # problem = get_or_None(session, db.Problem, source=source.id)
        problems = []
        premises = []
        conjectures = []
        if s_created:
            for line in self.load_expressions_from_file(path):
                if isinstance(line, logic.Import):
                    imported_source = (
                        session.query(db.Source).filter_by(path=line.path).first()
                    )
                    if imported_source:
                        axiomset = (
                            session.query(db.Formula)
                            .filter_by(source=imported_source)
                            .all()
                        )
                    else:
                        axiomset = self.axiomset_processor(
                            os.path.join(settings.TPTP_ROOT, line.path),
                            session=session,
                            commit=False,
                        )
                        # raise Exception("Source (%s) not found" % line.path)
                    for axiom in axiomset:
                        premises.append(axiom)
                elif isinstance(line, AnnotatedFormula):
                    if line.role in (
                        problem.FormulaRole.CONJECTURE,
                        problem.FormulaRole.NEGATED_CONJECTURE,
                    ):
                        conjecture = self.formula_processor(
                            line, *args, source=source, force_creation=True, **kwargs
                        )
                        session.add(conjecture)
                        conjectures.append(conjecture)
                    else:
                        premise = self.formula_processor(
                            line, *args, source=source, force_creation=True, **kwargs
                        )
                        session.add(premise)
                        premises.append(premise)
                else:
                    raise NotImplementedError
            for conjecture in conjectures:
                p = db.Problem(premises=premises, source=source, conjecture=conjecture)
                session.add(p)
                problems.append(p)
            session.commit()
            return problems
        else:
            return session.query(db.Problem).filter_by(source=source).all()

    def formula_processor(
        self, formula: AnnotatedFormula, *args, force_creation=False, **kwargs
    ):
        source = kwargs.get("source")
        session = kwargs.get("session")
        if force_creation or source.id is None:
            formula_obj = db.Formula(
                name=formula.name, source=source, json=self.compiler.visit(formula)
            )
            session.add(formula_obj)
        else:
            formula_obj = get_or_None(
                session, db.Formula, name=formula.name, source=source
            )
            if formula_obj is None:
                raise Exception
        return formula_obj

    @with_session
    def axiomset_processor(self, path, *args, **kwargs):
        session = kwargs.get("session")
        source, created = get_or_create(session, db.Source, path=path)
        commit = kwargs.get("commit", False)
        if created:
            result = [
                self.formula_processor(formula=item, source=source, *args, **kwargs)
                for item in self.load_expressions_from_file(path)
            ]
            if commit:
                session.commit()
            return result
        else:
            return session.query(db.Formula).filter_by(source=source).all()


class AutoencoderProcessor(TPTPParser):
    def formula_processor(self, formula, *args, orig=None, **kwargs):
        return formula


def all_axioms(processor):
    files = [
        "Axioms/HWC001-0.ax",
        "Axioms/SET001-2.ax",
        "Axioms/LAT001-4.ax",
        "Axioms/GRP003-0.ax",
        "Axioms/SET004-1.ax",
        "Axioms/COM001+1.ax",
        "Axioms/CAT003-0.ax",
        "Axioms/SYN000-0.ax",
        "Axioms/LCL007+5.ax",
        "Axioms/CSR003+3.ax",
        "Axioms/KLE001+1.ax",
        "Axioms/GEO006+5.ax",
        "Axioms/MED001+1.ax",
        "Axioms/GEO004+2.ax",
        "Axioms/HAL001+0.ax",
        "Axioms/SWV009+0.ax",
        "Axioms/PHI001^0.ax",
        "Axioms/LCL013^0.ax",
        "Axioms/LCL013^2.ax",
        "Axioms/GEO008+0.ax",
        "Axioms/SWV006-3.ax",
        "Axioms/CSR002+3.ax",
        "Axioms/GEO005-0.ax",
        "Axioms/HWV002-2.ax",
        "Axioms/HWV002-1.ax",
        "Axioms/HWV001-2.ax",
        "Axioms/LCL006+4.ax",
        "Axioms/LCL008^0.ax",
        "Axioms/KLE001+4.ax",
        # BUG: , 'Axioms/KRS001+0.ax',
        "Axioms/LCL007+1.ax",
        "Axioms/GEO001-1.ax",
        "Axioms/SWV005-1.ax",
        "Axioms/ALG002+0.ax",
        "Axioms/DAT004=0.ax",
        "Axioms/GRP008-0.ax",
        "Axioms/PUZ004-0.ax",
        "Axioms/GRP004-1.ax",
        "Axioms/RNG002-0.ax",
        "Axioms/SET008^2.ax",
        "Axioms/LDA001-0.ax",
        "Axioms/CSR001+0.ax",
        "Axioms/GEO006+0.ax",
        "Axioms/LCL012^0.ax",
        "Axioms/CAT002-0.ax",
        "Axioms/LAT002-0.ax",
        "Axioms/LAT006-1.ax",
        "Axioms/LCL009^0.ax",
        "Axioms/SET001-0.ax",
        "Axioms/SWV003+0.ax",
        "Axioms/HEN001-0.ax",
        "Axioms/SET006+4.ax",
        "Axioms/GRP008-1.ax",
        "Axioms/NUM001-2.ax",
        "Axioms/GEO006+3.ax",
        "Axioms/HWV001-1.ax",
        "Axioms/GEO004+3.ax",
        # "Axioms/MAT001^0.ax",
        "Axioms/MSC001-2.ax",
        "Axioms/GRP004-2.ax",
        "Axioms/RNG003-0.ax",
        "Axioms/HEN002-0.ax",
        # BUG: , 'Axioms/BIO001+0.ax',
        "Axioms/SET009^0.ax",
        "Axioms/HWV002-0.ax",
        "Axioms/SET008^0.ax",
        "Axioms/LCL006+2.ax",
        "Axioms/GEO010+1.ax",
        "Axioms/LAT001-0.ax",
        "Axioms/LCL001-2.ax",
        "Axioms/GEO006+6.ax",
        "Axioms/GEO002-0.ax",
        "Axioms/SWV007+4.ax",
        "Axioms/GEO006+2.ax",
        "Axioms/MGT001-0.ax",
        "Axioms/PUZ006+0.ax",
        "Axioms/SWV007+2.ax",
        "Axioms/SWB001+0.ax",
        "Axioms/LCL016^0.ax",
        "Axioms/SET004-0.ax",
        "Axioms/GEO004-2.ax",
        "Axioms/TOP001-0.ax",
        "Axioms/ANA001-0.ax",
        "Axioms/PLA001-1.ax",
        "Axioms/LCL004-1.ax",
        "Axioms/SWB002+0.ax",
        "Axioms/LCL007+4.ax",
        "Axioms/SWV004-0.ax",
        "Axioms/GEO003-0.ax",
        "Axioms/LCL013^5.ax",
        "Axioms/AGT001+1.ax",
        "Axioms/KLE001+7.ax",
        "Axioms/GRA001+0.ax",
        "Axioms/AGT001+0.ax",
        "Axioms/SET006+2.ax",
        "Axioms/KLE001+5.ax",
        "Axioms/GRP001-0.ax",
        "Axioms/MSC001-1.ax",
        "Axioms/PRD001+0.ax",
        "Axioms/LCL006+0.ax",
        "Axioms/DAT002=0.ax",
        "Axioms/SWV008^0.ax",
        "Axioms/SWV001-0.ax",
        "Axioms/SET006+1.ax",
        "Axioms/GEO002-2.ax",
        "Axioms/LCL007+3.ax",
        "Axioms/SWC001-0.ax",
        "Axioms/SET001-1.ax",
        "Axioms/SWV005-0.ax",
        "Axioms/LCL013^4.ax",
        "Axioms/KLE003+0.ax",
        "Axioms/FLD001-0.ax",
        "Axioms/GEO004-0.ax",
        "Axioms/KLE001+0.ax",
        "Axioms/SWV005-7.ax",
        "Axioms/NUM005+1.ax",
        "Axioms/GRP003+0.ax",
        "Axioms/GRP004-0.ax",
        "Axioms/COL002-0.ax",
        "Axioms/GEO002-3.ax",
        "Axioms/AGT001+2.ax",
        "Axioms/PUZ005+0.ax",
        "Axioms/SET006+0.ax",
        "Axioms/NUM005+0.ax",
        "Axioms/LCL013^6.ax",
        "Axioms/KLE004+0.ax",
        "Axioms/MGT001+0.ax",
        "Axioms/SWV007+1.ax",
        "Axioms/LCL014^0.ax",
        "Axioms/GRP003-1.ax",
        "Axioms/QUA001^1.ax",
        "Axioms/GEO004-3.ax",
        "Axioms/NUM001-1.ax",
        "Axioms/GRP004+0.ax",
        "Axioms/BOO002-0.ax",
        "Axioms/LAT001-1.ax",
        "Axioms/COM001+0.ax",
        "Axioms/GEO006+4.ax",
        "Axioms/SYN000_0.ax",
        "Axioms/ROB001-1.ax",
        "Axioms/LCL007+0.ax",
        "Axioms/GEO002-1.ax",
        "Axioms/LCL007+6.ax",
        "Axioms/SWV013-0.ax",
        "Axioms/SYN002+0.ax",
        "Axioms/NUM001-0.ax",
        "Axioms/BOO003-0.ax",
        "Axioms/SWV005-5.ax",
        "Axioms/REL001+0.ax",
        "Axioms/LCL007+2.ax",
        "Axioms/LAT004-0.ax",
        "Axioms/SWV005-6.ax",
        "Axioms/SET003-0.ax",
        "Axioms/HWV001-0.ax",
        "Axioms/RNG005-0.ax",
        # BUG:, 'Axioms/KRS001+1.ax',
        "Axioms/LCL001-1.ax",
        "Axioms/LAT001-2.ax",
        "Axioms/LCL003-0.ax",
        "Axioms/SWV002-0.ax",
        "Axioms/KLE001+2.ax",
        "Axioms/SWB003+1.ax",
        "Axioms/SWV005-2.ax",
        "Axioms/GEO004-1.ax",
        "Axioms/SWV007+3.ax",
        "Axioms/GEO004+0.ax",
        "Axioms/COL001-0.ax",
        "Axioms/KLE002+0.ax",
        "Axioms/KLE001+6.ax",
        "Axioms/GEO011+0.ax",
        "Axioms/SWV010^0.ax",
        "Axioms/SWV006-2.ax",
        "Axioms/CAT004-0.ax",
        "Axioms/GRP007+0.ax",
        "Axioms/GEO006+1.ax",
        "Axioms/NUM004-0.ax",
        "Axioms/GEO007+1.ax",
        "Axioms/SWV008^2.ax",
        "Axioms/LCL004-2.ax",
        "Axioms/SET008^1.ax",
        "Axioms/DAT006=0.ax",
        "Axioms/BOO004-0.ax",
        "Axioms/QUA001^0.ax",
        "Axioms/LCL016^1.ax",
        "Axioms/GRP005-0.ax",
        "Axioms/PLA001-0.ax",
        "Axioms/SWV005-4.ax",
        "Axioms/LCL004-0.ax",
        "Axioms/NUM003-0.ax",
        "Axioms/SET001-3.ax",
        "Axioms/KLE001+3.ax",
        "Axioms/SWV008^1.ax",
        "Axioms/DAT003=0.ax",
        "Axioms/SET006+3.ax",
        "Axioms/LCL006+1.ax",
        "Axioms/NUM005+2.ax",
        "Axioms/LCL010^0.ax",
        "Axioms/NUM002-0.ax",
        "Axioms/REL001-1.ax",
        "Axioms/DAT001=0.ax",
        "Axioms/LAT005-0.ax",
        "Axioms/BOO001-0.ax",
        "Axioms/ANA003-0.ax",
        "Axioms/LCL001-0.ax",
        "Axioms/SWV012+0.ax",
        "Axioms/LCL006+3.ax",
        "Axioms/GEO007+0.ax",
        "Axioms/SWB003+0.ax",
        "Axioms/LCL017^0.ax",
        "Axioms/LCL015^0.ax",
        "Axioms/LCL015^1.ax",
        "Axioms/LAT006-0.ax",
        "Axioms/PUZ002-0.ax",
        "Axioms/ANA002-0.ax",
        "Axioms/HWV004-0.ax",
        "Axioms/REL001+1.ax",
        "Axioms/SYN000^0.ax",
        "Axioms/LAT006-2.ax",
        "Axioms/LCL013^3.ax",
        "Axioms/LAT001-3.ax",
        "Axioms/PUZ001-0.ax",
        "Axioms/SET002-0.ax",
        "Axioms/SWV006-1.ax",
        "Axioms/PLA002+0.ax",
        "Axioms/LCL002-0.ax",
        "Axioms/SWV005-3.ax",
        "Axioms/SWV006-0.ax",
        "Axioms/REL001-0.ax",
        "Axioms/DAT002=1.ax",
        "Axioms/LCL011^0.ax",
        "Axioms/PUZ005-0.ax",
        "Axioms/GEO004+1.ax",
        "Axioms/LCL006+5.ax",
        "Axioms/ALG001-0.ax",
        "Axioms/HEN003-0.ax",
        "Axioms/PUZ003-0.ax",
        "Axioms/SWV011+0.ax",
        "Axioms/GRP006-0.ax",
        "Axioms/SWC001+0.ax",
        "Axioms/MSC001-0.ax",
        "Axioms/SYN001-0.ax",
        "Axioms/RNG001-0.ax",
        "Axioms/HWV003-0.ax",
        "Axioms/SWV007+0.ax",
        "Axioms/NUM006^0.ax",
        "Axioms/HWC002-0.ax",
        "Axioms/LAT003-0.ax",
        "Axioms/FLD002-0.ax",
        "Axioms/LCL013^1.ax",
        "Axioms/GEO009+0.ax",
        "Axioms/LCL002-1.ax",
        "Axioms/COL002-1.ax",
        "Axioms/GEO001-0.ax",
        "Axioms/CAT001-0.ax",
        "Axioms/SET005+0.ax",
        "Axioms/DAT005=0.ax",
        "Axioms/ROB001-0.ax",
        "Axioms/LCL005-0.ax",
        "Axioms/RNG004-0.ax",
        "Axioms/SYN000+0.ax",
        "Axioms/GRP002-0.ax",
        "Axioms/ALG003^0.ax",
        "Axioms/GRP003-2.ax",
        "Axioms/SET007/SET007+872.ax",
        "Axioms/SET007/SET007+598.ax",
        "Axioms/SET007/SET007+871.ax",
        "Axioms/SET007/SET007+529.ax",
        "Axioms/SET007/SET007+570.ax",
        "Axioms/SET007/SET007+408.ax",
        "Axioms/SET007/SET007+190.ax",
        "Axioms/SET007/SET007+209.ax",
        "Axioms/SET007/SET007+399.ax",
        "Axioms/SET007/SET007+2.ax",
        "Axioms/SET007/SET007+922.ax",
        "Axioms/SET007/SET007+747.ax",
        "Axioms/SET007/SET007+900.ax",
        "Axioms/SET007/SET007+811.ax",
        "Axioms/SET007/SET007+640.ax",
        "Axioms/SET007/SET007+916.ax",
        "Axioms/SET007/SET007+150.ax",
        "Axioms/SET007/SET007+244.ax",
        "Axioms/SET007/SET007+665.ax",
        "Axioms/SET007/SET007+582.ax",
        "Axioms/SET007/SET007+301.ax",
        "Axioms/SET007/SET007+398.ax",
        "Axioms/SET007/SET007+414.ax",
        "Axioms/SET007/SET007+420.ax",
        "Axioms/SET007/SET007+660.ax",
        "Axioms/SET007/SET007+734.ax",
        "Axioms/SET007/SET007+839.ax",
        "Axioms/SET007/SET007+56.ax",
        "Axioms/SET007/SET007+622.ax",
        "Axioms/SET007/SET007+254.ax",
        "Axioms/SET007/SET007+170.ax",
        "Axioms/SET007/SET007+642.ax",
        "Axioms/SET007/SET007+171.ax",
        "Axioms/SET007/SET007+432.ax",
        "Axioms/SET007/SET007+499.ax",
        "Axioms/SET007/SET007+210.ax",
        "Axioms/SET007/SET007+772.ax",
        "Axioms/SET007/SET007+633.ax",
        "Axioms/SET007/SET007+720.ax",
        "Axioms/SET007/SET007+455.ax",
        "Axioms/SET007/SET007+257.ax",
        "Axioms/SET007/SET007+714.ax",
        "Axioms/SET007/SET007+919.ax",
        "Axioms/SET007/SET007+779.ax",
        "Axioms/SET007/SET007+600.ax",
        "Axioms/SET007/SET007+344.ax",
        "Axioms/SET007/SET007+796.ax",
        "Axioms/SET007/SET007+809.ax",
        "Axioms/SET007/SET007+726.ax",
        "Axioms/SET007/SET007+744.ax",
        "Axioms/SET007/SET007+39.ax",
        "Axioms/SET007/SET007+865.ax",
        "Axioms/SET007/SET007+151.ax",
        "Axioms/SET007/SET007+235.ax",
        "Axioms/SET007/SET007+220.ax",
        "Axioms/SET007/SET007+503.ax",
        "Axioms/SET007/SET007+448.ax",
        "Axioms/SET007/SET007+904.ax",
        "Axioms/SET007/SET007+158.ax",
        "Axioms/SET007/SET007+338.ax",
        "Axioms/SET007/SET007+119.ax",
        "Axioms/SET007/SET007+705.ax",
        "Axioms/SET007/SET007+206.ax",
        "Axioms/SET007/SET007+827.ax",
        "Axioms/SET007/SET007+155.ax",
        "Axioms/SET007/SET007+626.ax",
        "Axioms/SET007/SET007+601.ax",
        "Axioms/SET007/SET007+153.ax",
        "Axioms/SET007/SET007+332.ax",
        "Axioms/SET007/SET007+116.ax",
        "Axioms/SET007/SET007+195.ax",
        "Axioms/SET007/SET007+778.ax",
        "Axioms/SET007/SET007+80.ax",
        "Axioms/SET007/SET007+434.ax",
        "Axioms/SET007/SET007+790.ax",
        "Axioms/SET007/SET007+853.ax",
        "Axioms/SET007/SET007+680.ax",
        "Axioms/SET007/SET007+316.ax",
        "Axioms/SET007/SET007+488.ax",
        "Axioms/SET007/SET007+712.ax",
        "Axioms/SET007/SET007+471.ax",
        "Axioms/SET007/SET007+90.ax",
        "Axioms/SET007/SET007+561.ax",
        "Axioms/SET007/SET007+550.ax",
        "Axioms/SET007/SET007+444.ax",
        "Axioms/SET007/SET007+129.ax",
        "Axioms/SET007/SET007+616.ax",
        "Axioms/SET007/SET007+409.ax",
        "Axioms/SET007/SET007+318.ax",
        "Axioms/SET007/SET007+586.ax",
        "Axioms/SET007/SET007+852.ax",
        "Axioms/SET007/SET007+699.ax",
        "Axioms/SET007/SET007+73.ax",
        "Axioms/SET007/SET007+57.ax",
        "Axioms/SET007/SET007+429.ax",
        "Axioms/SET007/SET007+585.ax",
        "Axioms/SET007/SET007+75.ax",
        "Axioms/SET007/SET007+866.ax",
        "Axioms/SET007/SET007+53.ax",
        "Axioms/SET007/SET007+212.ax",
        "Axioms/SET007/SET007+595.ax",
        "Axioms/SET007/SET007+178.ax",
        "Axioms/SET007/SET007+330.ax",
        "Axioms/SET007/SET007+26.ax",
        "Axioms/SET007/SET007+121.ax",
        "Axioms/SET007/SET007+468.ax",
        "Axioms/SET007/SET007+801.ax",
        "Axioms/SET007/SET007+903.ax",
        "Axioms/SET007/SET007+909.ax",
        "Axioms/SET007/SET007+232.ax",
        "Axioms/SET007/SET007+840.ax",
        "Axioms/SET007/SET007+287.ax",
        "Axioms/SET007/SET007+487.ax",
        "Axioms/SET007/SET007+505.ax",
        "Axioms/SET007/SET007+157.ax",
        "Axioms/SET007/SET007+216.ax",
        "Axioms/SET007/SET007+203.ax",
        "Axioms/SET007/SET007+722.ax",
        "Axioms/SET007/SET007+844.ax",
        "Axioms/SET007/SET007+379.ax",
        "Axioms/SET007/SET007+632.ax",
        "Axioms/SET007/SET007+438.ax",
        "Axioms/SET007/SET007+538.ax",
        "Axioms/SET007/SET007+282.ax",
        "Axioms/SET007/SET007+767.ax",
        "Axioms/SET007/SET007+423.ax",
        "Axioms/SET007/SET007+855.ax",
        "Axioms/SET007/SET007+89.ax",
        "Axioms/SET007/SET007+602.ax",
        "Axioms/SET007/SET007+66.ax",
        "Axioms/SET007/SET007+743.ax",
        "Axioms/SET007/SET007+321.ax",
        "Axioms/SET007/SET007+9.ax",
        "Axioms/SET007/SET007+882.ax",
        "Axioms/SET007/SET007+797.ax",
        "Axioms/SET007/SET007+194.ax",
        "Axioms/SET007/SET007+41.ax",
        "Axioms/SET007/SET007+461.ax",
        "Axioms/SET007/SET007+521.ax",
        "Axioms/SET007/SET007+638.ax",
        "Axioms/SET007/SET007+87.ax",
        "Axioms/SET007/SET007+706.ax",
        "Axioms/SET007/SET007+3.ax",
        "Axioms/SET007/SET007+393.ax",
        "Axioms/SET007/SET007+715.ax",
        "Axioms/SET007/SET007+342.ax",
        "Axioms/SET007/SET007+908.ax",
        "Axioms/SET007/SET007+307.ax",
        "Axioms/SET007/SET007+534.ax",
        "Axioms/SET007/SET007+345.ax",
        "Axioms/SET007/SET007+428.ax",
        "Axioms/SET007/SET007+667.ax",
        "Axioms/SET007/SET007+319.ax",
        "Axioms/SET007/SET007+300.ax",
        "Axioms/SET007/SET007+708.ax",
        "Axioms/SET007/SET007+285.ax",
        "Axioms/SET007/SET007+897.ax",
        "Axioms/SET007/SET007+164.ax",
        "Axioms/SET007/SET007+808.ax",
        "Axioms/SET007/SET007+620.ax",
        "Axioms/SET007/SET007+842.ax",
        "Axioms/SET007/SET007+389.ax",
        "Axioms/SET007/SET007+163.ax",
        "Axioms/SET007/SET007+635.ax",
        "Axioms/SET007/SET007+686.ax",
        "Axioms/SET007/SET007+662.ax",
        "Axioms/SET007/SET007+519.ax",
        "Axioms/SET007/SET007+243.ax",
        "Axioms/SET007/SET007+407.ax",
        "Axioms/SET007/SET007+187.ax",
        "Axioms/SET007/SET007+693.ax",
        "Axioms/SET007/SET007+42.ax",
        "Axioms/SET007/SET007+61.ax",
        "Axioms/SET007/SET007+740.ax",
        "Axioms/SET007/SET007+813.ax",
        "Axioms/SET007/SET007+695.ax",
        "Axioms/SET007/SET007+78.ax",
        "Axioms/SET007/SET007+552.ax",
        "Axioms/SET007/SET007+732.ax",
        "Axioms/SET007/SET007+553.ax",
        "Axioms/SET007/SET007+29.ax",
        "Axioms/SET007/SET007+161.ax",
        "Axioms/SET007/SET007+22.ax",
        "Axioms/SET007/SET007+666.ax",
        "Axioms/SET007/SET007+17.ax",
        "Axioms/SET007/SET007+918.ax",
        "Axioms/SET007/SET007+533.ax",
        "Axioms/SET007/SET007+281.ax",
        "Axioms/SET007/SET007+474.ax",
        "Axioms/SET007/SET007+62.ax",
        "Axioms/SET007/SET007+498.ax",
        "Axioms/SET007/SET007+314.ax",
        "Axioms/SET007/SET007+383.ax",
        "Axioms/SET007/SET007+196.ax",
        "Axioms/SET007/SET007+826.ax",
        "Axioms/SET007/SET007+925.ax",
        "Axioms/SET007/SET007+44.ax",
        "Axioms/SET007/SET007+239.ax",
        "Axioms/SET007/SET007+386.ax",
        "Axioms/SET007/SET007+86.ax",
        "Axioms/SET007/SET007+15.ax",
        "Axioms/SET007/SET007+895.ax",
        "Axioms/SET007/SET007+275.ax",
        "Axioms/SET007/SET007+451.ax",
        "Axioms/SET007/SET007+272.ax",
        "Axioms/SET007/SET007+664.ax",
        "Axioms/SET007/SET007+435.ax",
        "Axioms/SET007/SET007+179.ax",
        "Axioms/SET007/SET007+91.ax",
        "Axioms/SET007/SET007+673.ax",
        "Axioms/SET007/SET007+416.ax",
        "Axioms/SET007/SET007+639.ax",
        "Axioms/SET007/SET007+248.ax",
        "Axioms/SET007/SET007+637.ax",
        "Axioms/SET007/SET007+340.ax",
        "Axioms/SET007/SET007+142.ax",
        "Axioms/SET007/SET007+237.ax",
        "Axioms/SET007/SET007+803.ax",
        "Axioms/SET007/SET007+392.ax",
        "Axioms/SET007/SET007+396.ax",
        "Axioms/SET007/SET007+576.ax",
        "Axioms/SET007/SET007+439.ax",
        "Axioms/SET007/SET007+88.ax",
        "Axioms/SET007/SET007+927.ax",
        "Axioms/SET007/SET007+614.ax",
        "Axioms/SET007/SET007+905.ax",
        "Axioms/SET007/SET007+286.ax",
        "Axioms/SET007/SET007+898.ax",
        "Axioms/SET007/SET007+306.ax",
        "Axioms/SET007/SET007+229.ax",
        "Axioms/SET007/SET007+615.ax",
        "Axioms/SET007/SET007+149.ax",
        "Axioms/SET007/SET007+869.ax",
        "Axioms/SET007/SET007+671.ax",
        "Axioms/SET007/SET007+376.ax",
        "Axioms/SET007/SET007+260.ax",
        "Axioms/SET007/SET007+783.ax",
        "Axioms/SET007/SET007+222.ax",
        "Axioms/SET007/SET007+502.ax",
        "Axioms/SET007/SET007+685.ax",
        "Axioms/SET007/SET007+591.ax",
        "Axioms/SET007/SET007+261.ax",
        "Axioms/SET007/SET007+823.ax",
        "Axioms/SET007/SET007+608.ax",
        "Axioms/SET007/SET007+217.ax",
        "Axioms/SET007/SET007+46.ax",
        "Axioms/SET007/SET007+490.ax",
        "Axioms/SET007/SET007+888.ax",
        "Axioms/SET007/SET007+165.ax",
        "Axioms/SET007/SET007+663.ax",
        "Axioms/SET007/SET007+843.ax",
        "Axioms/SET007/SET007+525.ax",
        "Axioms/SET007/SET007+391.ax",
        "Axioms/SET007/SET007+305.ax",
        "Axioms/SET007/SET007+760.ax",
        "Axioms/SET007/SET007+531.ax",
        "Axioms/SET007/SET007+192.ax",
        "Axioms/SET007/SET007+670.ax",
        "Axioms/SET007/SET007+122.ax",
        "Axioms/SET007/SET007+571.ax",
        "Axioms/SET007/SET007+108.ax",
        "Axioms/SET007/SET007+298.ax",
        "Axioms/SET007/SET007+780.ax",
        "Axioms/SET007/SET007+765.ax",
        "Axioms/SET007/SET007+794.ax",
        "Axioms/SET007/SET007+127.ax",
        "Axioms/SET007/SET007+259.ax",
        "Axioms/SET007/SET007+466.ax",
        "Axioms/SET007/SET007+467.ax",
        "Axioms/SET007/SET007+403.ax",
        "Axioms/SET007/SET007+34.ax",
        "Axioms/SET007/SET007+506.ax",
        "Axioms/SET007/SET007+833.ax",
        "Axioms/SET007/SET007+183.ax",
        "Axioms/SET007/SET007+518.ax",
        "Axioms/SET007/SET007+623.ax",
        "Axioms/SET007/SET007+440.ax",
        "Axioms/SET007/SET007+290.ax",
        "Axioms/SET007/SET007+219.ax",
        "Axioms/SET007/SET007+230.ax",
        "Axioms/SET007/SET007+284.ax",
        "Axioms/SET007/SET007+141.ax",
        "Axioms/SET007/SET007+443.ax",
        "Axioms/SET007/SET007+40.ax",
        "Axioms/SET007/SET007+447.ax",
        "Axioms/SET007/SET007+856.ax",
        "Axioms/SET007/SET007+711.ax",
        "Axioms/SET007/SET007+96.ax",
        "Axioms/SET007/SET007+820.ax",
        "Axioms/SET007/SET007+5.ax",
        "Axioms/SET007/SET007+609.ax",
        "Axioms/SET007/SET007+269.ax",
        "Axioms/SET007/SET007+881.ax",
        "Axioms/SET007/SET007+924.ax",
        "Axioms/SET007/SET007+208.ax",
        "Axioms/SET007/SET007+628.ax",
        "Axioms/SET007/SET007+469.ax",
        "Axioms/SET007/SET007+477.ax",
        "Axioms/SET007/SET007+810.ax",
        "Axioms/SET007/SET007+176.ax",
        "Axioms/SET007/SET007+679.ax",
        "Axioms/SET007/SET007+19.ax",
        "Axioms/SET007/SET007+746.ax",
        "Axioms/SET007/SET007+617.ax",
        "Axioms/SET007/SET007+584.ax",
        "Axioms/SET007/SET007+876.ax",
        "Axioms/SET007/SET007+567.ax",
        "Axioms/SET007/SET007+60.ax",
        "Axioms/SET007/SET007+128.ax",
        "Axioms/SET007/SET007+563.ax",
        "Axioms/SET007/SET007+603.ax",
        "Axioms/SET007/SET007+539.ax",
        "Axioms/SET007/SET007+733.ax",
        "Axioms/SET007/SET007+483.ax",
        "Axioms/SET007/SET007+647.ax",
        "Axioms/SET007/SET007+650.ax",
        "Axioms/SET007/SET007+137.ax",
        "Axioms/SET007/SET007+198.ax",
        "Axioms/SET007/SET007+914.ax",
        "Axioms/SET007/SET007+459.ax",
        "Axioms/SET007/SET007+323.ax",
        "Axioms/SET007/SET007+485.ax",
        "Axioms/SET007/SET007+412.ax",
        "Axioms/SET007/SET007+700.ax",
        "Axioms/SET007/SET007+166.ax",
        "Axioms/SET007/SET007+829.ax",
        "Axioms/SET007/SET007+643.ax",
        "Axioms/SET007/SET007+462.ax",
        "Axioms/SET007/SET007+184.ax",
        "Axioms/SET007/SET007+289.ax",
        "Axioms/SET007/SET007+154.ax",
        "Axioms/SET007/SET007+304.ax",
        "Axioms/SET007/SET007+71.ax",
        "Axioms/SET007/SET007+807.ax",
        "Axioms/SET007/SET007+917.ax",
        "Axioms/SET007/SET007+368.ax",
        "Axioms/SET007/SET007+404.ax",
        "Axioms/SET007/SET007+651.ax",
        "Axioms/SET007/SET007+430.ax",
        "Axioms/SET007/SET007+333.ax",
        "Axioms/SET007/SET007+395.ax",
        "Axioms/SET007/SET007+283.ax",
        "Axioms/SET007/SET007+605.ax",
        "Axioms/SET007/SET007+928.ax",
        "Axioms/SET007/SET007+802.ax",
        "Axioms/SET007/SET007+51.ax",
        "Axioms/SET007/SET007+341.ax",
        "Axioms/SET007/SET007+775.ax",
        "Axioms/SET007/SET007+641.ax",
        "Axioms/SET007/SET007+380.ax",
        "Axioms/SET007/SET007+189.ax",
        "Axioms/SET007/SET007+65.ax",
        "Axioms/SET007/SET007+199.ax",
        "Axioms/SET007/SET007+390.ax",
        "Axioms/SET007/SET007+104.ax",
        "Axioms/SET007/SET007+676.ax",
        "Axioms/SET007/SET007+677.ax",
        "Axioms/SET007/SET007+636.ax",
        "Axioms/SET007/SET007+753.ax",
        "Axioms/SET007/SET007+508.ax",
        "Axioms/SET007/SET007+452.ax",
        "Axioms/SET007/SET007+263.ax",
        "Axioms/SET007/SET007+241.ax",
        "Axioms/SET007/SET007+785.ax",
        "Axioms/SET007/SET007+575.ax",
        "Axioms/SET007/SET007+348.ax",
        "Axioms/SET007/SET007+371.ax",
        "Axioms/SET007/SET007+581.ax",
        "Axioms/SET007/SET007+683.ax",
        "Axioms/SET007/SET007+139.ax",
        "Axioms/SET007/SET007+792.ax",
        "Axioms/SET007/SET007+546.ax",
        "Axioms/SET007/SET007+510.ax",
        "Axioms/SET007/SET007+147.ax",
        "Axioms/SET007/SET007+523.ax",
        "Axioms/SET007/SET007+787.ax",
        "Axioms/SET007/SET007+880.ax",
        "Axioms/SET007/SET007+535.ax",
        "Axioms/SET007/SET007+352.ax",
        "Axioms/SET007/SET007+687.ax",
        "Axioms/SET007/SET007+358.ax",
        "Axioms/SET007/SET007+28.ax",
        "Axioms/SET007/SET007+117.ax",
        "Axioms/SET007/SET007+336.ax",
        "Axioms/SET007/SET007+470.ax",
        "Axioms/SET007/SET007+296.ax",
        "Axioms/SET007/SET007+701.ax",
        "Axioms/SET007/SET007+657.ax",
        "Axioms/SET007/SET007+484.ax",
        "Axioms/SET007/SET007+204.ax",
        "Axioms/SET007/SET007+293.ax",
        "Axioms/SET007/SET007+188.ax",
        "Axioms/SET007/SET007+742.ax",
        "Axioms/SET007/SET007+49.ax",
        "Axioms/SET007/SET007+520.ax",
        "Axioms/SET007/SET007+661.ax",
        "Axioms/SET007/SET007+453.ax",
        "Axioms/SET007/SET007+850.ax",
        "Axioms/SET007/SET007+72.ax",
        "Axioms/SET007/SET007+426.ax",
        "Axioms/SET007/SET007+750.ax",
        "Axioms/SET007/SET007+43.ax",
        "Axioms/SET007/SET007+704.ax",
        "Axioms/SET007/SET007+812.ax",
        "Axioms/SET007/SET007+251.ax",
        "Axioms/SET007/SET007+594.ax",
        "Axioms/SET007/SET007+771.ax",
        "Axioms/SET007/SET007+781.ax",
        "Axioms/SET007/SET007+758.ax",
        "Axioms/SET007/SET007+655.ax",
        "Axioms/SET007/SET007+312.ax",
        "Axioms/SET007/SET007+549.ax",
        "Axioms/SET007/SET007+644.ax",
        "Axioms/SET007/SET007+696.ax",
        "Axioms/SET007/SET007+247.ax",
        "Axioms/SET007/SET007+421.ax",
        "Axioms/SET007/SET007+159.ax",
        "Axioms/SET007/SET007+335.ax",
        "Axioms/SET007/SET007+7.ax",
        "Axioms/SET007/SET007+85.ax",
        "Axioms/SET007/SET007+140.ax",
        "Axioms/SET007/SET007+381.ax",
        "Axioms/SET007/SET007+362.ax",
        "Axioms/SET007/SET007+713.ax",
        "Axioms/SET007/SET007+168.ax",
        "Axioms/SET007/SET007+558.ax",
        "Axioms/SET007/SET007+889.ax",
        "Axioms/SET007/SET007+400.ax",
        "Axioms/SET007/SET007+634.ax",
        "Axioms/SET007/SET007+495.ax",
        "Axioms/SET007/SET007+773.ax",
        "Axioms/SET007/SET007+793.ax",
        "Axioms/SET007/SET007+611.ax",
        "Axioms/SET007/SET007+899.ax",
        "Axioms/SET007/SET007+377.ax",
        "Axioms/SET007/SET007+310.ax",
        "Axioms/SET007/SET007+863.ax",
        "Axioms/SET007/SET007+883.ax",
        "Axioms/SET007/SET007+537.ax",
        "Axioms/SET007/SET007+82.ax",
        "Axioms/SET007/SET007+32.ax",
        "Axioms/SET007/SET007+543.ax",
        "Axioms/SET007/SET007+375.ax",
        "Axioms/SET007/SET007+68.ax",
        "Axioms/SET007/SET007+668.ax",
        "Axioms/SET007/SET007+213.ax",
        "Axioms/SET007/SET007+621.ax",
        "Axioms/SET007/SET007+148.ax",
        "Axioms/SET007/SET007+901.ax",
        "Axioms/SET007/SET007+294.ax",
        "Axioms/SET007/SET007+349.ax",
        "Axioms/SET007/SET007+800.ax",
        "Axioms/SET007/SET007+112.ax",
        "Axioms/SET007/SET007+832.ax",
        "Axioms/SET007/SET007+631.ax",
        "Axioms/SET007/SET007+249.ax",
        "Axioms/SET007/SET007+387.ax",
        "Axioms/SET007/SET007+245.ax",
        "Axioms/SET007/SET007+325.ax",
        "Axioms/SET007/SET007+92.ax",
        "Axioms/SET007/SET007+873.ax",
        "Axioms/SET007/SET007+926.ax",
        "Axioms/SET007/SET007+224.ax",
        "Axioms/SET007/SET007+912.ax",
        "Axioms/SET007/SET007+417.ax",
        "Axioms/SET007/SET007+337.ax",
        "Axioms/SET007/SET007+770.ax",
        "Axioms/SET007/SET007+821.ax",
        "Axioms/SET007/SET007+795.ax",
        "Axioms/SET007/SET007+324.ax",
        "Axioms/SET007/SET007+530.ax",
        "Axioms/SET007/SET007+835.ax",
        "Axioms/SET007/SET007+831.ax",
        "Axioms/SET007/SET007+846.ax",
        "Axioms/SET007/SET007+463.ax",
        "Axioms/SET007/SET007+458.ax",
        "Axioms/SET007/SET007+569.ax",
        "Axioms/SET007/SET007+460.ax",
        "Axioms/SET007/SET007+374.ax",
        "Axioms/SET007/SET007+134.ax",
        "Axioms/SET007/SET007+55.ax",
        "Axioms/SET007/SET007+449.ax",
        "Axioms/SET007/SET007+491.ax",
        "Axioms/SET007/SET007+589.ax",
        "Axioms/SET007/SET007+227.ax",
        "Axioms/SET007/SET007+95.ax",
        "Axioms/SET007/SET007+674.ax",
        "Axioms/SET007/SET007+817.ax",
        "Axioms/SET007/SET007+536.ax",
        "Axioms/SET007/SET007+911.ax",
        "Axioms/SET007/SET007+437.ax",
        "Axioms/SET007/SET007+649.ax",
        "Axioms/SET007/SET007+100.ax",
        "Axioms/SET007/SET007+551.ax",
        "Axioms/SET007/SET007+278.ax",
        "Axioms/SET007/SET007+526.ax",
        "Axioms/SET007/SET007+143.ax",
        "Axioms/SET007/SET007+522.ax",
        "Axioms/SET007/SET007+442.ax",
        "Axioms/SET007/SET007+132.ax",
        "Axioms/SET007/SET007+101.ax",
        "Axioms/SET007/SET007+654.ax",
        "Axioms/SET007/SET007+501.ax",
        "Axioms/SET007/SET007+185.ax",
        "Axioms/SET007/SET007+828.ax",
        "Axioms/SET007/SET007+532.ax",
        "Axioms/SET007/SET007+107.ax",
        "Axioms/SET007/SET007+120.ax",
        "Axioms/SET007/SET007+877.ax",
        "Axioms/SET007/SET007+557.ax",
        "Axioms/SET007/SET007+115.ax",
        "Axioms/SET007/SET007+527.ax",
        "Axioms/SET007/SET007+8.ax",
        "Axioms/SET007/SET007+624.ax",
        "Axioms/SET007/SET007+825.ax",
        "Axioms/SET007/SET007+878.ax",
        "Axioms/SET007/SET007+327.ax",
        "Axioms/SET007/SET007+11.ax",
        "Axioms/SET007/SET007+703.ax",
        "Axioms/SET007/SET007+496.ax",
        "Axioms/SET007/SET007+292.ax",
        "Axioms/SET007/SET007+497.ax",
        "Axioms/SET007/SET007+819.ax",
        "Axioms/SET007/SET007+858.ax",
        "Axioms/SET007/SET007+824.ax",
        "Axioms/SET007/SET007+277.ax",
        "Axioms/SET007/SET007+320.ax",
        "Axioms/SET007/SET007+606.ax",
        "Axioms/SET007/SET007+646.ax",
        "Axioms/SET007/SET007+566.ax",
        "Axioms/SET007/SET007+436.ax",
        "Axioms/SET007/SET007+353.ax",
        "Axioms/SET007/SET007+789.ax",
        "Axioms/SET007/SET007+59.ax",
        "Axioms/SET007/SET007+920.ax",
        "Axioms/SET007/SET007+299.ax",
        "Axioms/SET007/SET007+125.ax",
        "Axioms/SET007/SET007+406.ax",
        "Axioms/SET007/SET007+109.ax",
        "Axioms/SET007/SET007+256.ax",
        "Axioms/SET007/SET007+723.ax",
        "Axioms/SET007/SET007+450.ax",
        "Axioms/SET007/SET007+6.ax",
        "Axioms/SET007/SET007+77.ax",
        "Axioms/SET007/SET007+588.ax",
        "Axioms/SET007/SET007+252.ax",
        "Axioms/SET007/SET007+355.ax",
        "Axioms/SET007/SET007+14.ax",
        "Axioms/SET007/SET007+465.ax",
        "Axioms/SET007/SET007+697.ax",
        "Axioms/SET007/SET007+748.ax",
        "Axioms/SET007/SET007+784.ax",
        "Axioms/SET007/SET007+419.ax",
        "Axioms/SET007/SET007+30.ax",
        "Axioms/SET007/SET007+494.ax",
        "Axioms/SET007/SET007+763.ax",
        "Axioms/SET007/SET007+736.ax",
        "Axioms/SET007/SET007+741.ax",
        "Axioms/SET007/SET007+544.ax",
        "Axioms/SET007/SET007+270.ax",
        "Axioms/SET007/SET007+311.ax",
        "Axioms/SET007/SET007+69.ax",
        "Axioms/SET007/SET007+99.ax",
        "Axioms/SET007/SET007+366.ax",
        "Axioms/SET007/SET007+730.ax",
        "Axioms/SET007/SET007+253.ax",
        "Axioms/SET007/SET007+33.ax",
        "Axioms/SET007/SET007+757.ax",
        "Axioms/SET007/SET007+317.ax",
        "Axioms/SET007/SET007+18.ax",
        "Axioms/SET007/SET007+446.ax",
        "Axioms/SET007/SET007+394.ax",
        "Axioms/SET007/SET007+921.ax",
        "Axioms/SET007/SET007+884.ax",
        "Axioms/SET007/SET007+592.ax",
        "Axioms/SET007/SET007+702.ax",
        "Axioms/SET007/SET007+572.ax",
        "Axioms/SET007/SET007+98.ax",
        "Axioms/SET007/SET007+231.ax",
        "Axioms/SET007/SET007+480.ax",
        "Axioms/SET007/SET007+79.ax",
        "Axioms/SET007/SET007+23.ax",
        "Axioms/SET007/SET007+554.ax",
        "Axioms/SET007/SET007+818.ax",
        "Axioms/SET007/SET007+645.ax",
        "Axioms/SET007/SET007+754.ax",
        "Axioms/SET007/SET007+25.ax",
        "Axioms/SET007/SET007+359.ax",
        "Axioms/SET007/SET007+682.ax",
        "Axioms/SET007/SET007+885.ax",
        "Axioms/SET007/SET007+58.ax",
        "Axioms/SET007/SET007+175.ax",
        "Axioms/SET007/SET007+50.ax",
        "Axioms/SET007/SET007+724.ax",
        "Axioms/SET007/SET007+144.ax",
        "Axioms/SET007/SET007+516.ax",
        "Axioms/SET007/SET007+890.ax",
        "Axioms/SET007/SET007+745.ax",
        "Axioms/SET007/SET007+692.ax",
        "Axioms/SET007/SET007+492.ax",
        "Axioms/SET007/SET007+593.ax",
        "Axioms/SET007/SET007+776.ax",
        "Axioms/SET007/SET007+769.ax",
        "Axioms/SET007/SET007+454.ax",
        "Axioms/SET007/SET007+456.ax",
        "Axioms/SET007/SET007+20.ax",
        "Axioms/SET007/SET007+297.ax",
        "Axioms/SET007/SET007+433.ax",
        "Axioms/SET007/SET007+562.ax",
        "Axioms/SET007/SET007+509.ax",
        "Axioms/SET007/SET007+548.ax",
        "Axioms/SET007/SET007+799.ax",
        "Axioms/SET007/SET007+76.ax",
        "Axioms/SET007/SET007+725.ax",
        "Axioms/SET007/SET007+512.ax",
        "Axioms/SET007/SET007+816.ax",
        "Axioms/SET007/SET007+851.ax",
        "Axioms/SET007/SET007+879.ax",
        "Axioms/SET007/SET007+597.ax",
        "Axioms/SET007/SET007+618.ax",
        "Axioms/SET007/SET007+350.ax",
        "Axioms/SET007/SET007+672.ax",
        "Axioms/SET007/SET007+405.ax",
        "Axioms/SET007/SET007+574.ax",
        "Axioms/SET007/SET007+729.ax",
        "Axioms/SET007/SET007+211.ax",
        "Axioms/SET007/SET007+303.ax",
        "Axioms/SET007/SET007+814.ax",
        "Axioms/SET007/SET007+113.ax",
        "Axioms/SET007/SET007+200.ax",
        "Axioms/SET007/SET007+215.ax",
        "Axioms/SET007/SET007+891.ax",
        "Axioms/SET007/SET007+102.ax",
        "Axioms/SET007/SET007+160.ax",
        "Axioms/SET007/SET007+759.ax",
        "Axioms/SET007/SET007+360.ax",
        "Axioms/SET007/SET007+511.ax",
        "Axioms/SET007/SET007+242.ax",
        "Axioms/SET007/SET007+370.ax",
        "Axioms/SET007/SET007+372.ax",
        "Axioms/SET007/SET007+309.ax",
        "Axioms/SET007/SET007+441.ax",
        "Axioms/SET007/SET007+737.ax",
        "Axioms/SET007/SET007+36.ax",
        "Axioms/SET007/SET007+806.ax",
        "Axioms/SET007/SET007+727.ax",
        "Axioms/SET007/SET007+815.ax",
        "Axioms/SET007/SET007+857.ax",
        "Axioms/SET007/SET007+274.ax",
        "Axioms/SET007/SET007+97.ax",
        "Axioms/SET007/SET007+607.ax",
        "Axioms/SET007/SET007+367.ax",
        "Axioms/SET007/SET007+54.ax",
        "Axioms/SET007/SET007+38.ax",
        "Axioms/SET007/SET007+205.ax",
        "Axioms/SET007/SET007+564.ax",
        "Axioms/SET007/SET007+415.ax",
        "Axioms/SET007/SET007+236.ax",
        "Axioms/SET007/SET007+93.ax",
        "Axioms/SET007/SET007+315.ax",
        "Axioms/SET007/SET007+131.ax",
        "Axioms/SET007/SET007+373.ax",
        "Axioms/SET007/SET007+401.ax",
        "Axioms/SET007/SET007+410.ax",
        "Axioms/SET007/SET007+731.ax",
        "Axioms/SET007/SET007+418.ax",
        "Axioms/SET007/SET007+361.ax",
        "Axioms/SET007/SET007+555.ax",
        "Axioms/SET007/SET007+265.ax",
        "Axioms/SET007/SET007+596.ax",
        "Axioms/SET007/SET007+798.ax",
        "Axioms/SET007/SET007+804.ax",
        "Axioms/SET007/SET007+130.ax",
        "Axioms/SET007/SET007+678.ax",
        "Axioms/SET007/SET007+258.ax",
        "Axioms/SET007/SET007+52.ax",
        "Axioms/SET007/SET007+830.ax",
        "Axioms/SET007/SET007+238.ax",
        "Axioms/SET007/SET007+67.ax",
        "Axioms/SET007/SET007+424.ax",
        "Axioms/SET007/SET007+749.ax",
        "Axioms/SET007/SET007+782.ax",
        "Axioms/SET007/SET007+126.ax",
        "Axioms/SET007/SET007+652.ax",
        "Axioms/SET007/SET007+481.ax",
        "Axioms/SET007/SET007+191.ax",
        "Axioms/SET007/SET007+489.ax",
        "Axioms/SET007/SET007+822.ax",
        "Axioms/SET007/SET007+264.ax",
        "Axioms/SET007/SET007+849.ax",
        "Axioms/SET007/SET007+464.ax",
        "Axioms/SET007/SET007+579.ax",
        "Axioms/SET007/SET007+868.ax",
        "Axioms/SET007/SET007+834.ax",
        "Axioms/SET007/SET007+425.ax",
        "Axioms/SET007/SET007+540.ax",
        "Axioms/SET007/SET007+860.ax",
        "Axioms/SET007/SET007+276.ax",
        "Axioms/SET007/SET007+848.ax",
        "Axioms/SET007/SET007+1.ax",
        "Axioms/SET007/SET007+228.ax",
        "Axioms/SET007/SET007+625.ax",
        "Axioms/SET007/SET007+246.ax",
        "Axioms/SET007/SET007+659.ax",
        "Axioms/SET007/SET007+21.ax",
        "Axioms/SET007/SET007+10.ax",
        "Axioms/SET007/SET007+357.ax",
        "Axioms/SET007/SET007+202.ax",
        "Axioms/SET007/SET007+658.ax",
        "Axioms/SET007/SET007+755.ax",
        "Axioms/SET007/SET007+193.ax",
        "Axioms/SET007/SET007+103.ax",
        "Axioms/SET007/SET007+162.ax",
        "Axioms/SET007/SET007+735.ax",
        "Axioms/SET007/SET007+385.ax",
        "Axioms/SET007/SET007+83.ax",
        "Axioms/SET007/SET007+70.ax",
        "Axioms/SET007/SET007+124.ax",
        "Axioms/SET007/SET007+587.ax",
        "Axioms/SET007/SET007+4.ax",
        "Axioms/SET007/SET007+648.ax",
        "Axioms/SET007/SET007+63.ax",
        "Axioms/SET007/SET007+690.ax",
        "Axioms/SET007/SET007+118.ax",
        "Axioms/SET007/SET007+517.ax",
        "Axioms/SET007/SET007+322.ax",
        "Axioms/SET007/SET007+751.ax",
        "Axioms/SET007/SET007+493.ax",
        "Axioms/SET007/SET007+24.ax",
        "Axioms/SET007/SET007+268.ax",
        "Axioms/SET007/SET007+473.ax",
        "Axioms/SET007/SET007+886.ax",
        "Axioms/SET007/SET007+788.ax",
        "Axioms/SET007/SET007+180.ax",
        "Axioms/SET007/SET007+174.ax",
        "Axioms/SET007/SET007+568.ax",
        "Axioms/SET007/SET007+31.ax",
        "Axioms/SET007/SET007+719.ax",
        "Axioms/SET007/SET007+233.ax",
        "Axioms/SET007/SET007+225.ax",
        "Axioms/SET007/SET007+681.ax",
        "Axioms/SET007/SET007+838.ax",
        "Axioms/SET007/SET007+907.ax",
        "Axioms/SET007/SET007+226.ax",
        "Axioms/SET007/SET007+656.ax",
        "Axioms/SET007/SET007+547.ax",
        "Axioms/SET007/SET007+762.ax",
        "Axioms/SET007/SET007+577.ax",
        "Axioms/SET007/SET007+354.ax",
        "Axioms/SET007/SET007+887.ax",
        "Axioms/SET007/SET007+363.ax",
        "Axioms/SET007/SET007+902.ax",
        "Axioms/SET007/SET007+707.ax",
        "Axioms/SET007/SET007+214.ax",
        "Axioms/SET007/SET007+347.ax",
        "Axioms/SET007/SET007+356.ax",
        "Axioms/SET007/SET007+475.ax",
        "Axioms/SET007/SET007+786.ax",
        "Axioms/SET007/SET007+279.ax",
        "Axioms/SET007/SET007+630.ax",
        "Axioms/SET007/SET007+201.ax",
        "Axioms/SET007/SET007+81.ax",
        "Axioms/SET007/SET007+500.ax",
        "Axioms/SET007/SET007+698.ax",
        "Axioms/SET007/SET007+578.ax",
        "Axioms/SET007/SET007+47.ax",
        "Axioms/SET007/SET007+351.ax",
        "Axioms/SET007/SET007+146.ax",
        "Axioms/SET007/SET007+583.ax",
        "Axioms/SET007/SET007+504.ax",
        "Axioms/SET007/SET007+114.ax",
        "Axioms/SET007/SET007+197.ax",
        "Axioms/SET007/SET007+472.ax",
        "Axioms/SET007/SET007+413.ax",
        "Axioms/SET007/SET007+266.ax",
        "Axioms/SET007/SET007+255.ax",
        "Axioms/SET007/SET007+861.ax",
        "Axioms/SET007/SET007+382.ax",
        "Axioms/SET007/SET007+45.ax",
        "Axioms/SET007/SET007+273.ax",
        "Axioms/SET007/SET007+172.ax",
        "Axioms/SET007/SET007+560.ax",
        "Axioms/SET007/SET007+524.ax",
        "Axioms/SET007/SET007+862.ax",
        "Axioms/SET007/SET007+135.ax",
        "Axioms/SET007/SET007+326.ax",
        "Axioms/SET007/SET007+123.ax",
        "Axioms/SET007/SET007+94.ax",
        "Axioms/SET007/SET007+709.ax",
        "Axioms/SET007/SET007+106.ax",
        "Axioms/SET007/SET007+896.ax",
        "Axioms/SET007/SET007+738.ax",
        "Axioms/SET007/SET007+271.ax",
        "Axioms/SET007/SET007+145.ax",
        "Axioms/SET007/SET007+156.ax",
        "Axioms/SET007/SET007+710.ax",
        "Axioms/SET007/SET007+859.ax",
        "Axioms/SET007/SET007+694.ax",
        "Axioms/SET007/SET007+870.ax",
        "Axioms/SET007/SET007+27.ax",
        "Axioms/SET007/SET007+328.ax",
        "Axioms/SET007/SET007+841.ax",
        "Axioms/SET007/SET007+910.ax",
        "Axioms/SET007/SET007+689.ax",
        "Axioms/SET007/SET007+837.ax",
        "Axioms/SET007/SET007+111.ax",
        "Axioms/SET007/SET007+313.ax",
        "Axioms/SET007/SET007+329.ax",
        "Axioms/SET007/SET007+854.ax",
        "Axioms/SET007/SET007+378.ax",
        "Axioms/SET007/SET007+478.ax",
        "Axioms/SET007/SET007+653.ax",
        "Axioms/SET007/SET007+515.ax",
        "Axioms/SET007/SET007+48.ax",
        "Axioms/SET007/SET007+573.ax",
        "Axioms/SET007/SET007+684.ax",
        "Axioms/SET007/SET007+613.ax",
        "Axioms/SET007/SET007+590.ax",
        "Axioms/SET007/SET007+545.ax",
        "Axioms/SET007/SET007+291.ax",
        "Axioms/SET007/SET007+234.ax",
        "Axioms/SET007/SET007+331.ax",
        "Axioms/SET007/SET007+717.ax",
        "Axioms/SET007/SET007+346.ax",
        "Axioms/SET007/SET007+105.ax",
        "Axioms/SET007/SET007+791.ax",
        "Axioms/SET007/SET007+218.ax",
        "Axioms/SET007/SET007+221.ax",
        "Axioms/SET007/SET007+169.ax",
        "Axioms/SET007/SET007+110.ax",
        "Axioms/SET007/SET007+845.ax",
        "Axioms/SET007/SET007+457.ax",
        "Axioms/SET007/SET007+136.ax",
        "Axioms/SET007/SET007+295.ax",
        "Axioms/SET007/SET007+12.ax",
        "Axioms/SET007/SET007+280.ax",
        "Axioms/SET007/SET007+402.ax",
        "Axioms/SET007/SET007+427.ax",
        "Axioms/SET007/SET007+610.ax",
        "Axioms/SET007/SET007+894.ax",
        "Axioms/SET007/SET007+923.ax",
        "Axioms/SET007/SET007+223.ax",
        "Axioms/SET007/SET007+565.ax",
        "Axioms/SET007/SET007+482.ax",
        "Axioms/SET007/SET007+308.ax",
        "Axioms/SET007/SET007+186.ax",
        "Axioms/SET007/SET007+718.ax",
        "Axioms/SET007/SET007+629.ax",
        "Axioms/SET007/SET007+0.ax",
        "Axioms/SET007/SET007+181.ax",
        "Axioms/SET007/SET007+369.ax",
        "Axioms/SET007/SET007+84.ax",
        "Axioms/SET007/SET007+397.ax",
        "Axioms/SET007/SET007+182.ax",
        "Axioms/SET007/SET007+167.ax",
        "Axioms/SET007/SET007+37.ax",
        "Axioms/SET007/SET007+875.ax",
        "Axioms/SET007/SET007+542.ax",
        "Axioms/SET007/SET007+388.ax",
        "Axioms/SET007/SET007+612.ax",
        "Axioms/SET007/SET007+431.ax",
        "Axioms/SET007/SET007+339.ax",
        "Axioms/SET007/SET007+761.ax",
        "Axioms/SET007/SET007+267.ax",
        "Axioms/SET007/SET007+675.ax",
        "Axioms/SET007/SET007+867.ax",
        "Axioms/SET007/SET007+138.ax",
        "Axioms/SET007/SET007+559.ax",
        "Axioms/SET007/SET007+240.ax",
        "Axioms/SET007/SET007+514.ax",
        "Axioms/SET007/SET007+604.ax",
        "Axioms/SET007/SET007+16.ax",
        "Axioms/SET007/SET007+528.ax",
        "Axioms/SET007/SET007+764.ax",
        "Axioms/SET007/SET007+915.ax",
        "Axioms/SET007/SET007+752.ax",
        "Axioms/SET007/SET007+479.ax",
        "Axioms/SET007/SET007+384.ax",
        "Axioms/SET007/SET007+688.ax",
        "Axioms/SET007/SET007+334.ax",
        "Axioms/SET007/SET007+302.ax",
        "Axioms/SET007/SET007+691.ax",
        "Axioms/SET007/SET007+541.ax",
        "Axioms/SET007/SET007+768.ax",
        "Axioms/SET007/SET007+739.ax",
        "Axioms/SET007/SET007+177.ax",
        "Axioms/SET007/SET007+556.ax",
        "Axioms/SET007/SET007+486.ax",
        "Axioms/SET007/SET007+580.ax",
        "Axioms/SET007/SET007+445.ax",
        "Axioms/SET007/SET007+847.ax",
        "Axioms/SET007/SET007+716.ax",
        "Axioms/SET007/SET007+728.ax",
        "Axioms/SET007/SET007+207.ax",
        "Axioms/SET007/SET007+913.ax",
        "Axioms/SET007/SET007+133.ax",
        "Axioms/SET007/SET007+152.ax",
        "Axioms/SET007/SET007+756.ax",
        "Axioms/SET007/SET007+805.ax",
        "Axioms/SET007/SET007+766.ax",
        "Axioms/SET007/SET007+599.ax",
        "Axioms/SET007/SET007+411.ax",
        "Axioms/SET007/SET007+721.ax",
        "Axioms/SET007/SET007+669.ax",
        "Axioms/SET007/SET007+250.ax",
        "Axioms/SET007/SET007+892.ax",
        "Axioms/SET007/SET007+422.ax",
        "Axioms/SET007/SET007+906.ax",
        "Axioms/SET007/SET007+288.ax",
        "Axioms/SET007/SET007+774.ax",
        "Axioms/SET007/SET007+262.ax",
        "Axioms/SET007/SET007+777.ax",
        "Axioms/SET007/SET007+864.ax",
        "Axioms/SET007/SET007+619.ax",
        "Axioms/SET007/SET007+343.ax",
        "Axioms/SET007/SET007+929.ax",
        "Axioms/SET007/SET007+476.ax",
        "Axioms/SET007/SET007+513.ax",
        "Axioms/SET007/SET007+64.ax",
        "Axioms/SET007/SET007+364.ax",
        "Axioms/SET007/SET007+35.ax",
        "Axioms/SET007/SET007+893.ax",
        "Axioms/SET007/SET007+874.ax",
        "Axioms/SET007/SET007+627.ax",
        "Axioms/SET007/SET007+836.ax",
        "Axioms/SET007/SET007+13.ax",
        "Axioms/SET007/SET007+173.ax",
        "Axioms/SET007/SET007+507.ax",
        "Axioms/SET007/SET007+74.ax",
        "Axioms/SET007/SET007+365.ax",
        "Axioms/GEO010+0.ax",
        #'Axioms/CSR002+5.ax',
        # "Axioms/CSR003+2.ax",
        "Axioms/CSR001+2.ax",
        "Axioms/CSR001+3.ax",
        "Axioms/CSR004+0.ax",
        "Axioms/CSR001+1.ax",
        "Axioms/CSR003+0.ax",
        "Axioms/CSR003+5.ax",
        "Axioms/CSR003+4.ax",
        "Axioms/CSR002+0.ax",
        "Axioms/CSR002+1.ax",
        "Axioms/CSR005^0.ax",
        "Axioms/CSR002+4.ax",
        "Axioms/CSR003+1.ax",
        "Axioms/CSR002+2.ax",
        "Axioms/NLP001+0.ax",
        "Axioms/MED001+0.ax",
        "Axioms/MED002+0.ax",
    ]
    for f in files:
        print(f)
        processor.axiomset_processor(os.path.join(settings.TPTP_ROOT, f))


class TPTPProblemParser(ProblemParser):
    logic_parser_cls = TPTPParser


class SimpleTPTPProofParser(ProofParser):
    def __init__(self):
        self._tptp_parser = TPTPParser()

    def parse(self, structure: str, *args, **kwargs):
        return LinearProof(
            steps=[
                self._create_proof_step(s)
                for s in self._tptp_parser.load_many(structure.split("\n"))
            ]
        )

    def _create_proof_step(self, e: LogicElement) -> ProofStep:
        if isinstance(e, AnnotatedFormula):
            if e.role == FormulaRole.AXIOM:
                return Axiom(formula=e.formula, name=e.name)
            elif e.role == FormulaRole.PLAIN:
                if isinstance(e.annotation, InferenceSource):
                    return Inference(
                        formula=e.formula, name=e.name, antecedents=e.annotation.parents
                    )
                elif isinstance(e.annotation, InternalSource):
                    return Introduction(
                        formula=e.formula,
                        name=e.name,
                        introduction_type=e.annotation.intro_type,
                    )
            raise ParserException(e)
        else:
            raise ParserException


def get_all_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file == "README":
                yield os.path.join(root, file)


def all_problems(processor):
    for f in get_all_files(os.path.join(settings.TPTP_ROOT, "Problems")):
        print(f)
        for problem in processor.problem_processor(f):
            print("done")


def all_solution(path, system=""):
    path = os.path.join(path, "Problems")
    files = get_all_files(path)
    for file in files:
        domain, problem = os.path.normpath(file).split(os.sep)[-2:]
        response = requests.get(
            "http://www.tptp.org/cgi-bin/SeeTPTP?Category=Solutions"
            "&Domain={domain}"
            "&File={problem}"
            "&System=Vampire---4.3.THM-Ref.s".format(
                domain=domain, problem=problem[:-2]
            )
        )
        print(response)


def store_problems():
    processor = StorageProcessor()
    all_problems(processor)


def store_axioms():
    processor = StorageProcessor()
    all_axioms(processor)
