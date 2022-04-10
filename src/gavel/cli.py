"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m gavel` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``gavel.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``gavel.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import click
import os
import pkg_resources
from gavel.dialects.tptp.dialect import TPTPDialect

from gavel.dialects.tptp.parser import TPTPParser, TPTPProblemParser
from gavel.prover.hets.interface import HetsProve, HetsSession, HetsEngine
from gavel.prover.registry import get_prover
from gavel.selection.selector import Sine
from gavel.dialects.base.dialect import get_dialect, _DIALECT_REGISTRY
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


@click.command(name='translate', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument("frm")
@click.argument("to")
@click.argument("path")
@click.option("--save", "-s", metavar="SAVE_PATH", default="", help="If set, saves the translation to SAVE_PATH")
@click.option("--shorten-names", "-n", is_flag=True, help="Shorten names in output language (only for TPTP)")
@click.option("--no-annotations", "-a", is_flag=True, help="Remove annotations in output dialect")
@click.pass_context
def translate(ctx, frm, to, path, save, shorten_names, no_annotations):
    """
    Translates the file at PATH from the dialect specified by FRM to the dialect TO. You can get a list of all available dialects via the `dialects` command.

    Example usage:

        python -m gavel translate --save=my-output.p tptp tptp my-input-file.tptp

        This will parse a given TPTP-file into gavels internal logic and save a new equivalent TPTP theory in my-output.txt.
    """
    # allow for arguments with variable number of values
    index = 0
    kwargs = {}
    while index < len(ctx.args):
        if ctx.args[index].startswith('-'):
            command = ctx.args[index].strip('-')
            values = []
            index += 1
            while index < len(ctx.args) and not ctx.args[index].startswith('-'):
                values.append(ctx.args[index])
                index += 1

            kwargs[command] = values
        else:
            index += 1

    input_dialect = get_dialect(frm)
    output_dialect = get_dialect(to)

    parser = input_dialect._parser_cls()
    compiler = output_dialect._compiler_cls(shorten_names=(to == TPTPDialect._identifier() and shorten_names),
                                            keep_annotations=not no_annotations)

    # if the parameter save is specified, the translation gets saved as a file with that name
    translation = compiler.visit(parser.parse_from_file(path, **kwargs))
    if save != "":
        with open(str(save), 'w') as file:
            file.write(translation)
    else:
        print(translation)

    if frm == "annotated-owl" and to == TPTPDialect._identifier() and "save-dol" in kwargs:
        ontology_text = parser.ontology_text_dol
        parser_mapping = parser.name_mapping
        compiler_mapping = compiler.name_mapping

        owl_reserved = ['string', 'integer', 'decimal', 'float', 'Datatype', 'Class', 'ObjectProperty', 'DataProperty',
                        'AnnotationProperty', 'NamedIndividual', 'Annotations', 'Prefix', 'Ontology', 'Import',
                        'inverse', 'or', 'and', 'not', 'length', 'minLength', 'maxLength', 'pattern', 'langRange', '<=',
                        '<', '>=', '>', 'some', 'that', 'only', 'value', 'Self', 'min', 'max', 'exactly',
                        'EquivalentTo', 'SubClassOf', 'DisjointWith', 'DisjointUnionOf', 'HasKey', 'Domain', 'Range',
                        'Characteristics', 'SubPropertyOf', 'InverseOf', 'SubPropertyChain', 'Functional',
                        'InverseFunctional', 'Reflexive', 'Irreflexive', 'Symmetric', 'Asymmetric', 'Transitive',
                        'Types', 'Facets', 'SameAs', 'DifferentFrom', 'EquivalentClasses', 'DisjointClasses',
                        'EquivalentProperties', 'DisjointProperties', 'SameIndividual', 'DifferentIndividuals']

        dol_text = f'logic OWL\n' \
                   f'ontology OWL_ontology = \n' \
            # f'\t<{parser.ontology_iri}>\n' \

        dol_text += ontology_text
        #with open(path, 'r') as file:
        #    for line in file.readlines():
        #        dol_text += f'\t\t{line}'

        dol_text += f'\n\nend\n' \
                    f'\n' \
                    f'ontology TPTP_ontology = \n' \
                    f'\t OWL_ontology with \n'
        for i, key in enumerate(parser_mapping):
            tptp_name = key
            if key in compiler_mapping:
                tptp_name = compiler_mapping[key]
            if tptp_name != parser_mapping[key]:
                dol_text += '\t\t'
                # comment out lines containing reserved words
                if tptp_name in owl_reserved:
                    dol_text += '%%'
                    print(f'[Warning] "{tptp_name}" is a reserved OWL keyword '
                          f'and has been commented out in the DOL file.')
                dol_text += f'{parser_mapping[key]} |-> {tptp_name},\n'
        # remove last comma
        split = dol_text.rsplit(',', 1)
        dol_text = ''.join(split)

        dol_text += '\twith translation OWL22CASL, translation CASL2TPTP_FOF\n' \
                    '\tthen logic TPTP :\n'
        annot_axioms = translation.splitlines()
        i = 0
        while i < len(annot_axioms):
            i += 1
            line = annot_axioms[i]
            i += 1
            if not (line.startswith('fof(annotation_axiom') or line.startswith('%')):
                break
            dol_text += f'\t\t{line}\n'
        dol_text += 'end'

        if len(kwargs["save-dol"]) == 0:
            raise Exception('You have to provide a file name for the --save-dol option')

        with open(kwargs["save-dol"][0], 'w') as file:
            file.write(dol_text)


@click.command()
def dialects():
    for key in _DIALECT_REGISTRY.keys():
        print(key)


def add_source(source):
    global cli
    cli.add_source(source)


base.add_command(prove)
base.add_command(translate)
base.add_command(dialects)

cli = click.CommandCollection()

main = cli

cli.add_source(base)
for entry_point in pkg_resources.iter_entry_points("cli"):
    ep = entry_point.load()
    cli.add_source(ep)

if __name__ == "__main__":
    cli()
