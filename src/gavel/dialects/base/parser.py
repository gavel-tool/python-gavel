from typing import Generic
from typing import Iterable
from typing import TypeVar

from gavel.logic.base import LogicElement
from gavel.logic.base import Problem
from gavel.logic.base import Sentence

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

    def load_string(self, string: str, *args, **kwargs) -> Parseable:
        """
        Load a string into the structure represented by the dialect
        Parameters
        ----------
        string
        args
        kwargs
        Returns
        -------
        """
        raise NotImplementedError

    def load_many(self, string: Iterable[str])->Iterable[Parseable]:
        raise NotImplementedError


    def parse_from_string(
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
        args
        kwargs
        Returns
        -------
        """
        return self.parse(
            self.load_string(string, *(load_args or []), **(load_kwargs or {})),
            *(parse_args or []),
            **(parse_kwargs or {})
        )

    @staticmethod
    def __unpack_file(*args, **kwargs) -> str:
        """
        Parameters
        ----------
        Returns
        -------
        """
        with open(*args, **kwargs) as inp:
            return inp.read()

    def parse_from_file(self, file_path, *args, **kwargs) -> LogicElement:
        return self.parse_from_string(self.__unpack_file(file_path), *args, **kwargs)

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
        return self.is_valid(self.__unpack_file(*args, **kwargs))


class LogicParser(Parser[Parseable, Iterable[LogicElement]]):
    pass


class ProblemParser(Parser[Parseable, Problem]):
    logic_parser_cls = LogicParser

    def __init__(self, *args, **kwargs):
        self.logic_parser = LogicParser(*args, **kwargs)

    def parse(self, structure: Parseable, *args, **kwargs):
        premises = []
        conjectures = []
        for s in self.logic_parser.parse(structure):
            if isinstance(s, Sentence):
                if s.is_conjecture():
                    conjectures.append(s)
                else:
                    premises.append(s)
        for c in conjectures:
            yield Problem(premises, c)
