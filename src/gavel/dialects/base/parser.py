from abc import ABC
from typing import Generic
from typing import Iterable
from typing import TypeVar

from gavel.logic.logic import LogicElement
from gavel.logic.problem import Problem
from gavel.logic.problem import Sentence, Import
from gavel.logic.solution import Proof

import multiprocessing as mp

Parseable = TypeVar("Parseable")
Target = TypeVar("Target")


class Parser(Generic[Parseable, Target]):
    def parse(self, structure: Parseable, *args, **kwargs) -> Iterable[Target]:
        """
        Transforms the input structure into metadata as used by the
        OpenEnergyPlatform

        Parameters
        ----------

        inp: str
            The input string that should be parsed into OEP metadata

        Returns
        -------

        OEPMetadata
            OEP metadata represented by `inp`
        """
        raise NotImplementedError


class StringBasedParser(Parser[str, Target], ABC):
    @staticmethod
    def _unpack_file(*args, **kwargs) -> str:
        """
        Parameters
        ----------
        Returns
        -------
        """
        with open(*args, **kwargs) as inp:
            return inp.read()

    def parse_from_file(self, file_path, *args, **kwargs) -> Iterable[Target]:
        return self.parse(self._unpack_file(file_path))

    def is_valid(self, inp: str) -> bool:
        """
        Verify if `inp` is a sting representation that is parsable by this
        parser
        Parameters
        ----------
        inp: str
            String to verify
        Returns
        -------
        bool:
            Indicated whether this object is parsable or not
        """
        try:
            self.parse(inp)
        except:
            return False
        return True

    def is_file_valid(self, *args, **kwargs):
        return self.is_valid(self._unpack_file(*args, **kwargs))  #


class LogicParser(Parser[Parseable, LogicElement], ABC):
    pass


class ProblemParser(Parser[Parseable, Problem]):
    logic_parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        self.logic_parser = self.logic_parser_cls(*args, **kwargs)

    def parse(self, inp, *args, **kwargs):
        premises = []
        conjectures = []
        imports = []

        for s in self.logic_parser.parse(inp):
            if isinstance(s, Sentence):
                if s.is_conjecture():
                    conjectures.append(s)
                else:
                    premises.append(s)
            elif isinstance(s, Import):
                imports.append(s)
            else:
                raise ParserException("Unknown element:" + str(s))
        return Problem(premises, conjectures, imports)


class ParserException(Exception):
    pass


class ProofParser(Parser[Parseable, Proof]):
    pass
