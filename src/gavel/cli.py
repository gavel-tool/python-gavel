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
import gavel.language.tptp.build as build_tptp
import gavel.settings as settings


@click.group()
def db():
    pass


@click.command()
def initdb():
    """Create tables for storage of formulas"""
    fol_db.create_tables()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_tptp(p):
    settings.TPTP_ROOT = p
    build_tptp.store_tptp()


@click.command()
def cleardb():
    """Drop tables created gy initdb"""
    fol_db.drop_tables()


db.add_command(initdb)
db.add_command(cleardb)
db.add_command(store_tptp)

cli = click.CommandCollection(sources=[db])


if __name__ == "__main__":
    db()
