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
import pkg_resources

from gavel.dialects.tptp.parser import TPTPParser, TPTPProblemParser
from gavel.prover.hets.interface import HetsProve, HetsSession, HetsEngine
from gavel.prover.registry import get_prover
from gavel.selection.selector import Sine
from gavel.dialects.base.dialect import get_dialect
from gavel import plugins


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
        problem = processor.parse(fp.read())
        if s is not None:
            selector = Sine()
            problem = selector.select(problem)
        proof = prover.prove(problem)
        if not plot:
            for s in proof.steps:
                print("{name}: {formula}".format(name=s.name, formula=s.formula))
        else:
            g = proof.get_graph()
            g.render()


@click.command()
@click.argument("frm")
@click.argument("to")
@click.argument("path")
def translate(frm, to, path):
    input_dialect = get_dialect(frm)
    output_dialect = get_dialect(to)

    parser = input_dialect._parser_cls()
    compiler = output_dialect._compiler_cls()
    with open(path, "r") as finp:
        print(compiler.visit(parser.parse(finp.read())))


def add_source(source):
    global cli
    cli.add_source(source)


base.add_command(prove)
base.add_command(translate)

cli = click.CommandCollection()

main = cli


cli.add_source(base)
for entry_point in pkg_resources.iter_entry_points("cli"):
    ep = entry_point.load()
    cli.add_source(ep)

if __name__ == "__main__":
    cli()
