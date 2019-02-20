import os
from antlr4 import *
from .parser.tptp_v7_0_0_0Lexer import tptp_v7_0_0_0Lexer
from .parser.tptp_v7_0_0_0Parser import tptp_v7_0_0_0Parser
from .parser.flattening import FOFFlatteningVisitor
import chisel.io.structures as db
from chisel.logic import fol
import pickle as pkl
import sys
from chisel.language.base.compiler import Compiler
from chisel.io.connection import get_or_create, with_session, get_engine
from sqlalchemy.orm.session import sessionmaker

sys.setrecursionlimit(10000)
TPTP_ROOT = '/data/TPTP/'

class Processor:

    def folder_processor(self, path, file_processor, *args, **kwargs):
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file =='README':
                    f = os.path.join(root,file)
                    yield file_processor(f, *args, **kwargs)

    def problemset_processor(self, *args, **kwargs):
        return self.folder_processor(os.path.join(TPTP_ROOT, 'Problems'),
                                     self.problem_processor)

    def axiomsets_processor(self, *args, **kwargs):
        return self.folder_processor(os.path.join(TPTP_ROOT, 'Axioms'),
                                     self.axiomset_processor)

    def axiomset_processor(self, path, *args, **kwargs):
        for item in self.load_expressions_from_file(path):
            yield self.formula_processor(item, *args, **kwargs)

    def formula_processor(self, formula, *args, **kwargs):
        compiler = Compiler()
        return compiler.visit(formula)

    def load_expressions_from_file(self, path, *args, **kwargs):
        print(path)
        input = FileStream(TPTP_ROOT+path, encoding='utf8')
        lexer = tptp_v7_0_0_0Lexer(input)
        stream = CommonTokenStream(lexer)
        print('initialise parser...')
        parser = tptp_v7_0_0_0Parser(stream)
        print('done')
        print('build parse tree...')
        visitor = FOFFlatteningVisitor()
        # result = visitor.visit(parser.tptp_file())
        tree = parser.tptp_input()
        i=0
        while tree:
            i += 1
            if i%10000==0:
                print(i, tree.getText())
            try:
                yield self.syntax_tree_processor(tree, visitor, *args, **kwargs)
            except fol.EOFException:
                tree = None
            else:
                tree = parser.tptp_input()

    def syntax_tree_processor(self, tree, visitor, *args, **kwargs):
        return visitor.visit(tree)

    def file_processor(self, path, *args, **kwargs):
        return self.load_expressions_from_file(path, *args, **kwargs)

    def problem_processor(self, path, *args, **kwargs):
        for line in self.load_expressions_from_file(path, *args, **kwargs):
            yield self.formula_processor(line)


class StorageProcessor(Processor):

    @with_session
    def problem_processor(self, path, *args, **kwargs):
        session = kwargs.get('session')
        source, s_created = get_or_create(session, db.Source, path=path)
        problem, p_create = get_or_create(session, db.Problem, source=source.id)
        if p_create:
            for line in self.load_expressions_from_file(path):
                if isinstance(line, fol.Import):
                    imported_source = session.query(db.Source).filter_by(path=line.path).first()
                    if imported_source:
                        for axiom in session.query(db.Formula).filter_by(source=imported_source.id):
                            problem.premises.append(axiom)
                    else:
                        raise Exception('Source (%s) not found'%line.path)
                elif isinstance(line, fol.AnnotatedFormula):
                    if line.role == fol.FormulaRole.CONJECTURE:
                        conjecture = self.formula_processor(line, *args, source=source, **kwargs)
                        problem.conjecture = conjecture.id
                    else:
                        axiom = self.formula_processor(line, *args, source=source, **kwargs)
                        problem.premises.append(axiom)
                else:
                    raise NotImplementedError
            session.add(problem)
            session.commit()

    def formula_processor(self, formula: fol.AnnotatedFormula, *args, **kwargs):
        source = kwargs.get('source')
        session = kwargs.get('session')
        formula_obj, created = get_or_create(session, db.Formula, name=formula.name, source=source.id)
        if created:
            formula_obj.blob = pkl.dumps(formula)
        return formula_obj

    @with_session
    def axiomset_processor(self, path, *args, **kwargs):
        session = kwargs.get('session')
        source, created = get_or_create(session, db.Source, path=path)
        if created:
            for item in self.load_expressions_from_file(path):
                self.formula_processor(item, source=source, *args, **kwargs)
            session.commit()


