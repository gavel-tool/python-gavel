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
import os

import gavel.config.settings as settings
from gavel.dialects.db.structures import store_formula, create_tables, drop_tables
import gavel.dialects.tptp.parser as build_tptp
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.db.compiler import DBCompiler
from gavel.dialects.tptp.parser import Problem
from gavel.dialects.tptp.parser import TPTPParser
from gavel.prover.hets.interface import HetsProve
from gavel.prover.vampire.interface import VampireInterface
from gavel.selection.selector import Sine


@click.group()
def db():
    pass


@click.command()
def init_db():
    """Create tables for storage of formulas"""
    create_tables()


@click.command()
@click.argument("path", default=None)
@click.option("-r", default=False)
def store(path, r):
    parser = TPTPParser()
    compiler = DBCompiler()
    for sub_path in os.listdir(path):
        sub_path = os.path.join(path, sub_path)
        if os.path.isfile(sub_path):
            print(sub_path)
            i = 0
            for formula in parser.parse_from_file(sub_path):
                i += 1
                struc = compiler.visit(formula)
                store_formula(sub_path, struc)
            print("--- %d formulas extracted ---"%i)
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
    drop_tables()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def clear_db(p):
    """Drop tables created gy init-db and recreate them"""
    drop_tables()
    create_tables()


@click.command()
@click.argument("f")
@click.option("-s", default=None)
def prove(f, s):
    processor = TPTPParser()
    vp = VampireInterface()
    hp = HetsProve(vp)
    problems = list(processor.problem_processor(f))
    compiler = TPTPCompiler()
    for problem in problems:
        if s is not None:
            selector = Sine(
                premises=problem.premises, conjecture=problem.conjecture, max_depth=10
            )
            problem = Problem(premises=selector.select(), conjecture=problem.conjecture)
        proof = hp.prove(problem, compiler)
        for s in proof.steps:
            print(
                "{name}: {formula} [{source}]".format(
                    name=s.name, formula=s.formula, source=s.render_source()
                )
            )


@click.command()
@click.argument("f")
def select(f):
    processor = TPTPParser()
    problem = list(processor.problem_processor(f))[0]
    selector = Sine(
        premises=problem.premises, conjecture=problem.conjecture, max_depth=10
    )
    smaller_problem = Problem(premises=selector.select(), conjecture=problem.conjecture)
    for prem in list(smaller_problem.premises):
        print(prem)
    print(smaller_problem.conjecture)


db.add_command(init_db)
db.add_command(drop_db)
db.add_command(clear_db)
db.add_command(store_problems)
db.add_command(store)
db.add_command(store_solutions)

db.add_command(prove)

db.add_command(select)

cli = click.CommandCollection(sources=[db])

main = cli

if __name__ == "__main__":
    cli()
