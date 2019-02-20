import os
from antlr4 import *
from .parser.tptp_v7_0_0_0Lexer import tptp_v7_0_0_0Lexer
from .parser.tptp_v7_0_0_0Parser import tptp_v7_0_0_0Parser
from .parser.flattening import FOFFlatteningVisitor
import chisel.io.structures as db
from chisel.logic import fol
import pickle as pkl
import sys


sys.setrecursionlimit(10000)
TPTP_ROOT = '/data/TPTP/'

def load_folder(Session, path, processor):
    session = Session()
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file =='README':
                    f = os.path.join(root,file)
                    processor(session, f)
                session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def load_problems():
    return load_folder('data/TPTP/Problems', load_problem)


def load_problem(Session, path):
    path = path.replace('data/TPTP/', '')
    session = Session()
    try:
        source, s_created = get_or_create(session, db.Source, path=path)
        problem, p_create = get_or_create(session, db.Problem, source=source.id)
        if p_create:
            for line in load_file(path):
                if isinstance(line, fol.Import):
                    imported_source = session.query(db.Source).filter_by(path=line.path).first()
                    if imported_source:
                        for axiom in session.query(db.Formula).filter_by(source=imported_source.id):
                            problem.premises.append(axiom)
                    else:
                        raise Exception('Source (%s) not found'%line.path)
                elif isinstance(line, fol.AnnotatedFormula):
                    if line.role == fol.FormulaRole.CONJECTURE:
                        conjecture = store_formula(session, line, source=source)
                        problem.conjecture = conjecture.id
                    else:
                        axiom = store_formula(session, line, source=source)
                        problem.premises.append(axiom)
                else:
                    raise NotImplementedError
            session.add(problem)
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()







def store_formula(session, formula: fol.AnnotatedFormula, source):
    formula_obj, created = get_or_create(session, db.Formula, name=formula.name, source=source.id)
    if created:
        formula_obj.blob = pkl.dumps(formula)
    return formula_obj


def load_axiomsets():
    load_folder('data/TPTP/Axioms', load_axiomset)


def load_axiomset(Session, path):
    path=path.replace('data/TPTP/','')
    session = Session()
    try:
        source, created = get_or_create(session, db.Source, path=path)
        if created:
            for item in load_file(path):
                store_formula(session, item, source=source)
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def load_file(path):
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
    done = False
    i=0
    while tree and not done:
        i += 1
        if i%10000==0:
            print(i, tree.getText())
        try:
            formula = visitor.visit(tree)
            assert isinstance(formula, fol.AnnotatedFormula), type(formula)
            yield formula
        except fol.EOFException:
            done = True
        else:
            tree = parser.tptp_input()

def get_or_create(session, cls, **kwargs):
    obj = session.query(cls).filter_by(**kwargs).first()
    created = False
    if not obj:
        obj = cls(**kwargs)
        session.add(obj)
        created = True
    return obj, created
