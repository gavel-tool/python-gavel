"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mgavel` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``gavel.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``gavel.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import click

import gavel.dialects.db.structures as fol_db
import gavel.dialects.tptp.parser as build_tptp
import gavel.settings as settings
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import TPTPParser
from gavel.prover.hets.interface import HetsProve
from gavel.prover.vampire.interface import VampireInterface

@click.group()
def db():
    pass


@click.command()
def init_db():
    """Create tables for storage of formulas"""
    fol_db.create_tables()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_tptp(p):
    settings.TPTP_ROOT = p
    build_tptp.store_axioms()
    build_tptp.store_problems()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_problems(p):
    settings.TPTP_ROOT = p
    build_tptp.store_problems()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_solutions(p):
    """Drop tables created gy init-db"""
    build_tptp.all_solution(p)


@click.command()
def drop_db():
    """Drop tables created gy init-db"""
    fol_db.drop_tables()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def clear_db(p):
    """Drop tables created gy init-db and recreate them"""
    fol_db.drop_tables()
    fol_db.create_tables()


@click.command()
@click.argument("f")
def prove(f):
    processor = TPTPParser()
    vp = VampireInterface()
    hp = HetsProve(vp)
    problems = list(processor.problem_processor(f))
    compiler = TPTPCompiler()
    for problem in problems:
        for goal_result in hp.prove(problem, compiler):
            print(goal_result)


db.add_command(init_db)
db.add_command(drop_db)
db.add_command(clear_db)
db.add_command(store_problems)
db.add_command(store_tptp)
db.add_command(store_solutions)

db.add_command(prove)

cli = click.CommandCollection(sources=[db])

main = cli

if __name__ == "__main__":
    cli()
