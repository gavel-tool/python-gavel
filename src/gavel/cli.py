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

from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import Problem
from gavel.dialects.tptp.parser import TPTPParser, TPTPProblemParser
from gavel.prover.hets.interface import HetsProve, HetsSession, HetsEngine
from gavel.prover.registry import get_prover
from gavel.selection.selector import Sine
from alembic import command
from alembic.config import Config

ROOT_DIR = os.path.dirname(__file__)

alembic_cfg = Config(os.path.join(ROOT_DIR, "alembic.ini"))
alembic_cfg.set_main_option("script_location", os.path.join(ROOT_DIR, "alembic"))

@click.group()
def base():
    pass

@click.command()
@click.argument("p")
@click.argument("f")
@click.option("-s", default=None)
@click.option("--hets", is_flag=True, default=False)
@click.option("--plot", is_flag=True, default=False)
def prove(p, f, s, plot, hets):
    prover_interface = get_prover(p)
    prover = prover_interface()
    if hets:
        hets_engine = HetsEngine()
        hets_session = HetsSession(hets_engine)
        prover = HetsProve(prover, hets_session)

    processor = TPTPProblemParser()
    with open(f) as fp:
        problems = list(processor.parse(fp.readlines()))
    for problem in problems:
        if s is not None:
            selector = Sine()
            problem = selector.select(problem)
        proof = prover.prove(problem)
        if not plot:
            for s in proof.steps:
                print(
                    "{name}: {formula}".format(
                        name=s.name, formula=s.formula
                    )
                )
        else:
            g = proof.get_graph()
            g.render()

base.add_command(prove)

cli = click.CommandCollection()
cli.add_source(base)

main = cli

if __name__ == "__main__":
    cli()
