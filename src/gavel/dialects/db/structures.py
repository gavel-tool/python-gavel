import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship
from gavel.dialects.db.connection import with_session, get_or_create, get_or_None
from gavel.logic.problem import AnnotatedFormula

import os
import multiprocessing as mp

Base = declarative_base()


class Source(Base):
    __tablename__ = "source"
    id = sqla.Column(sqla.Integer, primary_key=True)
    path = sqla.Column(sqla.String, unique=True)
    complete = sqla.Column(sqla.Boolean, default=False)


class Formula(Base):
    __tablename__ = "formula"
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Text)
    source_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id), nullable=False)
    source = relationship(Source)
    logic = sqla.VARCHAR(4)
    json = sqla.Column(sqla.JSON)


association_premises = sqla.Table(
    "association",
    Base.metadata,
    sqla.Column("left_id", sqla.Integer, sqla.ForeignKey("problem.id"), nullable=False),
    sqla.Column(
        "right_id", sqla.Integer, sqla.ForeignKey("formula.id"), nullable=False
    ),
)


class SolutionItem(Base):
    id = sqla.Column(sqla.Integer, primary_key=True)
    __tablename__ = "solution_item"
    solution_id = sqla.Column(
        sqla.Integer, sqla.ForeignKey("solution.id"), nullable=False
    )
    solution = relationship("Solution")
    premise_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Formula.id), nullable=False)
    premise = relationship(Formula)
    used = sqla.Column(sqla.Boolean)


class Problem(Base):
    __tablename__ = "problem"
    id = sqla.Column(sqla.Integer, primary_key=True)
    source_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id), nullable=False)
    source = relationship(Source)
    conjecture_id = sqla.Column(
        sqla.Integer, sqla.ForeignKey(Formula.id), nullable=False
    )
    conjecture = relationship(Formula)
    premises = relation(Formula, secondary=association_premises)
    solutions = relation("Solution")

    def create_problem_file(self, file):
        for premise in self.premises:
            file.write(premise.original)


class Solution(Base):
    __tablename__ = "solution"
    id = sqla.Column(sqla.Integer, primary_key=True)
    problem_id = sqla.Column(sqla.Integer, sqla.ForeignKey("problem.id"))
    problem = relationship(Problem)
    premises = relation(SolutionItem)


@with_session
def store_formula(source, struc: AnnotatedFormula, session=None):
    source, created = get_or_create(session, Source, path=source)
    structure = None
    # If the source object was already in the database, the formula might
    # already be present, too. Check that before storing a second copy
    if not created:
        structure = get_or_None(session, Formula, name=struc.name, source=source)
    if structure is None:
        struc.source = source
        session.add(struc)
        session.commit()
        return True
    else:
        return False


def store_all(path, parser, compiler):
    if os.path.isdir(path):
        for sub_path in os.listdir(path):
            sub_path = os.path.join(path, sub_path)
            if os.path.isfile(sub_path):
                store_file(sub_path, parser, compiler)
    elif os.path.isfile(path):
        store_file(path, parser, compiler)


def store_file(path, parser, compiler):
    skip = False
    skip_reason = None
    print(path)
    if "=" not in path and "^" not in path:
        if not is_source_complete(path):
            i = 0
            pool = mp.Pool(mp.cpu_count() - 1)
            for struc in pool.imap(parser.parse_single_from_string, parser.stream_formulas(path)):
                i += 1
                store_formula(path, compiler.visit(struc))
            mark_source_complete(path)
            print("--- %d formulas extracted ---" % i)
            pool.close()
        else:
            skip = True
            skip_reason = "Already complete"
    else:
        skip = True
        skip_reason = "Not supported"
    if skip:
        print("--- Skipping - Reason: %s ---" % skip_reason)


@with_session
def mark_source_complete(source, session=None):
    session.query(Source).filter_by(path=source).update({"complete": True})
    session.commit()


@with_session
def is_source_complete(source, session=None):
    source_obj = get_or_None(session, Source, path=source)
    if source_obj is None:
        return False
    return source_obj.complete
