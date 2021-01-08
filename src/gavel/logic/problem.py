from enum import Enum
from typing import Iterable

from gavel.logic.logic import LogicElement
from gavel.logic.solution import ProofStep


class ProblemElement:
    pass


class Sentence(ProblemElement):
    def is_conjecture(self):
        raise NotImplementedError


class FormulaRole(Enum):

    __visit_name__ = "formula_role"

    AXIOM = 0
    HYPOTHESIS = 1
    DEFINITION = 2
    ASSUMPTION = 3
    LEMMA = 4
    THEOREM = 5
    COROLLARY = 6
    CONJECTURE = 7
    PLAIN = 8
    FINITE_INTERPRETATION_DOMAIN = 9
    FINITE_INTERPRETATION_FUNCTORS = 10
    FINITE_INTERPRETATION_PREDICATES = 11
    UNKNOWN = 12
    TYPE = 13
    NEGATED_CONJECTURE = 14

    def __repr__(self):
        return self.name


class AnnotatedFormula(Sentence, ProofStep):
    __visit_name__ = "annotated_formula"

    def __init__(
        self,
        logic,
        name: str = None,
        role: FormulaRole = None,
        formula: LogicElement = None,
        annotation=None,
    ):
        self.logic = logic
        self.name = name
        self.role = role
        self.formula = formula
        self.annotation = annotation

    def symbols(self):
        return self.formula.symbols()

    def is_conjecture(self):
        return self.role in (FormulaRole.CONJECTURE, FormulaRole.NEGATED_CONJECTURE)

    def __str__(self):
        return "{logic}({name},{role},{formula})".format(
            logic=self.logic, name=self.name, role=self.role, formula=self.formula
        ) + (("# " + str(self.annotation)) if self.annotation else "")

    def __eq__(self, other):
        return type(self) == type(other) and all(
            getattr(self, n) == getattr(other, n) for n in self.__dict__
        )

    def is_axiom(self):
        return self.role in [FormulaRole.AXIOM, FormulaRole.HYPOTHESIS, FormulaRole.ASSUMPTION]



class Import(ProblemElement):

    __visit_name__ = "import"

    def __init__(self, path, filter=None):
        self.path = path.replace("'", "")
        self.filter = filter


class Problem:
    """
    This class stores the important information that are needed for a proof

    Attributes
    ----------

    premises: :class:`gavel.logic.logic.Sentence`
        The premises available for this problem

    conjecture: :class:`gavel.logic.logic.Sentence`
        The conjecture that should be proven`
    """

    __visit_name__ = "problem"

    def __init__(
        self, premises: Iterable[Sentence], conjectures: Iterable[Sentence], imports=None
    ):
        self.premises = premises
        self.conjectures = conjectures
        self.imports = imports or []


class Annotation:
    def __init__(self):
        pass
