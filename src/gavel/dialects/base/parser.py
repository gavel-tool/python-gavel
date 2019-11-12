from abc import ABC
from typing import Generic
from typing import Iterable
from typing import TypeVar

from gavel.logic.logic import LogicElement
from gavel.logic.problem import Problem
from gavel.logic.problem import Sentence
from gavel.logic.proof import Proof

Parseable = TypeVar("Parseable")
Target = TypeVar("Target")


class Parser(Generic[Parseable, Target]):
    def parse(self, structure: Parseable, *args, **kwargs) -> Target:
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


class StringBasedParser(Parser, ABC):
    def load_single_from_string(self, string: str, *args, **kwargs) -> Parseable:
        """
        Load a string into the structure represented by the dialect

        Parameters
        ----------
        string

        Returns
        -------
        """
        raise NotImplementedError

    def parse_single_from_string(
        self,
        string: str,
        load_args=None,
        parse_args=None,
        load_kwargs=None,
        parse_kwargs=None,
    ) -> Target:
        """
        Parse a string into OEPMetadata

        Parameters
        ----------

        string

        Returns
        -------
        """
        return self.parse(
            self.load_single_from_string(
                string, *(load_args or []), **(load_kwargs or {})
            ),
            *(parse_args or []),
            **(parse_kwargs or {})
        )

    @staticmethod
    def _unpack_file(*args, **kwargs) -> Iterable[str]:
        """
        Parameters
        ----------
        Returns
        -------
        """
        with open(*args, **kwargs) as inp:
            return inp.readlines()

    def parse_from_file(self, file_path, *args, **kwargs) -> Iterable[Target]:
        for line in self.load_many(self._unpack_file(file_path)):
            yield self.parse(line, *args, **kwargs)

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
        raise NotImplementedError

    def is_file_valid(self, *args, **kwargs):
        return self.is_valid(self.__unpack_file(*args, **kwargs))  #

    def stream_formula_lines(self, lines: Iterable[str], **kwargs):
        raise NotImplementedError

    def stream_formulas(self, path, *args, **kwargs):
        return self.stream_formula_lines(self._unpack_file(path))

    def load_many(
        self, lines: Iterable[str], *args, **kwargs
    ) -> Iterable[LogicElement]:
        return map(
            self.load_single_from_string, self.stream_formula_lines(lines, **kwargs)
        )


class LogicParser(Parser[Parseable, LogicElement]):
    pass


class ProblemParser(Parser[Parseable, Problem]):
    logic_parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        self.logic_parser = self.logic_parser_cls(*args, **kwargs)

    def parse(self, inp, *args, **kwargs):
        premises = []
        conjectures = []
        for s in map(self.logic_parser.parse_single_from_string, self.logic_parser.stream_formula_lines(inp)):
            if isinstance(s, Sentence):
                if s.is_conjecture():
                    conjectures.append(s)
                else:
                    premises.append(s)
            else:
                raise ParserException("Unknown element:" + str(s))
        for c in conjectures:
            yield Problem(premises, c)


class ParserException(Exception):
    pass


class ProofParser(Parser[Parseable, Proof]):
    pass
