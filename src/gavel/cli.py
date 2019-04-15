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
import gavel.io.structures as fol_db
import gavel.language.tptp.processor as build_tptp
import gavel.settings as settings


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


db.add_command(init_db)
db.add_command(drop_db)
db.add_command(clear_db)
db.add_command(store_problems)
db.add_command(store_tptp)
db.add_command(store_solutions)


cli = click.CommandCollection(sources=[db])


if __name__ == "__main__":
    cli()
