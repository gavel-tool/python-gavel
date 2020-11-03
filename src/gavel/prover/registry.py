PROVERS = {}


def register_prover(name):
    """
    A class wrapper that registers a class under `name`. Thereafter this
    prover is known for the remaining execution and can be accessed via
    `get_prover` or in the commandline interface using its name.
    :param name: Identifier for this prover
    """

    def register_class(cls):
        PROVERS[name] = cls
        return cls

    return register_class


def get_prover(name):
    """
    Returns a registered prover identified by `name`.
    :param name:  Identifier of some prover
    :return: The prover associated with `name`
    """
    return PROVERS[name]


__all__ = ["get_prover", "register_prover"]
