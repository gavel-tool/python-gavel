from gavel.dialects.base.dialect import ProofElement
from typing import Iterable


class Annotation(ProofElement):
    pass


class Source(ProofElement):
    def __init__(self):
        pass

class InternalSource(Source):
    pass

class InferenceSource(Source):
    def __init__(self, rule, parents:Iterable[Source]):
        self.rule = rule
        self.parents = parents


class Input(Annotation):
    pass
