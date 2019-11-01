
PROVERS = {}


def register_prover(name):
    def register_class(cls):
        PROVERS[name] = cls
        return cls
    return register_class
