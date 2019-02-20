import enum
import sqlalchemy as sqla
from sqlalchemy.orm import relation
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base
from .connection import get_engine


Base = declarative_base()

class Source(Base):
    __tablename__='source'
    id = sqla.Column(sqla.Integer, primary_key=True)
    path = sqla.Column(sqla.String, unique=True)

class Formula(Base):
    __tablename__= 'formula'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Text)
    source = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id))
    blob = sqla.Column(sqla.Binary)
    __table_args__ = (sqla.UniqueConstraint('name', 'source', name='_form_name_source'),
                      )

association_premises = sqla.Table('association', Base.metadata,
    sqla.Column('left_id', sqla.Integer, sqla.ForeignKey('problem.id')),
    sqla.Column('right_id', sqla.Integer, sqla.ForeignKey('formula.id'))
)

class SolutionItem(Base):
    id = sqla.Column(sqla.Integer, primary_key=True)
    __tablename__ = 'solution_item'
    solution = sqla.Column(sqla.Integer, sqla.ForeignKey('solution.id'))
    premise = sqla.Column(sqla.Integer, sqla.ForeignKey(Formula.id))
    used = sqla.Column(sqla.Boolean)


class Problem(Base):
    __tablename__ = 'problem'
    id = sqla.Column(sqla.Integer, primary_key=True)
    source = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id))
    conjecture = sqla.Column(sqla.Integer, sqla.ForeignKey(Formula.id))
    premises = relation(Formula, secondary=association_premises)
    solutions = relation('Solution')


class Solution(Base):
    __tablename__ = 'solution'
    id = sqla.Column(sqla.Integer, primary_key=True)
    problem = sqla.Column(sqla.Integer, sqla.ForeignKey('problem.id'))
    premises = relation(SolutionItem)


def create_tables():
    print('Build datastructures')
    metadata = Base.metadata
    metadata.bind = get_engine()
    metadata.create_all()


def drop_tables(tables=None):
    print('Destroy datastructures')
    metadata = Base.metadata
    metadata.bind = get_engine()
    metadata.drop_all(tables=tables,)
