import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship

from gavel.dialects.db.connection import get_engine

Base = declarative_base()


class Source(Base):
    __tablename__ = "source"
    id = sqla.Column(sqla.Integer, primary_key=True)
    path = sqla.Column(sqla.String, unique=True)


class Formula(Base):
    __tablename__ = "formula"
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Text)
    source_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id), nullable=False)
    source = relationship(Source)
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


def create_tables():
    print("Build datastructures")
    metadata = Base.metadata
    metadata.bind = get_engine()
    metadata.create_all()


def drop_tables(tables=None):
    print("Destroy datastructures")
    metadata = Base.metadata
    metadata.bind = get_engine()
    metadata.drop_all(tables=tables)
