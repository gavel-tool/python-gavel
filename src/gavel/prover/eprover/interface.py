from gavel.prover.registry import register_prover
from gavel.dialects.base.dialect import Problem
from gavel.dialects.tptp.dialect import TPTPProofDialect
from gavel.prover.base.interface import BaseProverInterface
from gavel.prover.base.interface import BaseResultHandler
import subprocess as sub
import tempfile
import os


class EDialect(TPTPProofDialect):
    def parse(self, obj, *args, **kwargs):
        cleaned_obj = "\n".join(
            line for line in obj.split("\n") if not line.startswith("#")
        )
        return super(EDialect, self).parse(cleaned_obj, *args, **kwargs)


@register_prover("eprover")
class EProverInterface(BaseProverInterface):
    _prover_dialect_cls = EDialect

    def _bootstrap_problem(self, problem: Problem):
        problem_string = "\n".join(self.dialect.compile(l) for l in problem.premises)
        for conjecture in problem.conjectures:
            problem_string += self.dialect.compile(conjecture)
        return problem_string

    def _submit_problem(self, problem_instance, *args, **kwargs):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(problem_instance.encode())
            tf.seek(0)
            result = sub.check_output(
                [
                    os.environ.get("EPROVER", "eprover"),
                    "--output-level=2",
                    "--tptp-in",
                    "--tstp-out",
                    tf.name,
                ]
            ).decode("utf-8")
        return result


class ResultHandler(BaseResultHandler):
    def get_used_axioms(self):
        raise NotImplementedError
