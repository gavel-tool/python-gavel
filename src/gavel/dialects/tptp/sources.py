from typing import Iterable

from gavel.logic.proof import IntroductionType


class Annotation:
    pass


class Source:
    pass


class InternalSource(Source):
    def __init__(self, intro_type: IntroductionType, info):
        self.intro_type = intro_type
        self.info = info


class InferenceSource(Source):
    def __init__(self, rule, info, parents: Iterable[Source]):
        self.rule = rule
        self.info = info
        self.parents = parents


class FileSource(Source):
    def __init__(self, path, info):
        self.path = path
        self.info = info


class CreatorSource(Source):
    def __init__(self, creator):
        self.creator = creator


class TheorySource(Source):
    def __init__(self, theory):
        self.theory = theory


class Input(Annotation):
    pass
