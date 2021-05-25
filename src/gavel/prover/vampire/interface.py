import re

from gavel.prover.registry import register_prover
from gavel.logic.logic import PredefinedConstant
from gavel.dialects.base.dialect import Problem
from gavel.dialects.tptp.dialect import TPTPProofDialect
from gavel.prover.base.interface import BaseProverInterface
from gavel.prover.base.interface import BaseResultHandler
import subprocess as sub
import tempfile
import os

@register_prover("vampire")
class VampireInterface(BaseProverInterface):
    _prover_dialect_cls = TPTPProofDialect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = ["-t 300", "-p tptp"]

    def _bootstrap_problem(self, problem: Problem):
        problem_string = "\n".join(self.dialect.compile(l) for l in problem.premises)
        for imp in problem.imports:
            with open(imp.path) as impf:
                problem_string += impf.read()

        for conjecture in problem.conjectures:
            problem_string += self.dialect.compile(conjecture)
        if len(problem.conjectures) == 1 and problem.conjectures[0].formula == PredefinedConstant.FALSUM:
            mode = "--mode casc_sat"
        else:
            mode = "--mode casc"
        self.flags = [mode] + self.flags
        return problem_string

    def _submit_problem(self, problem_instance, *args, **kwargs):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(problem_instance.encode())
            tf.seek(0)
            try:
                result = sub.check_output(
                    " ".join([
                        os.environ.get("VAMPIRE", "vampire"),
                        *self.flags,
                        tf.name,
                    ]), shell=True).decode("utf-8")
            except sub.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return result

    def _post_process_proof(self, raw_proof_result):
        match = re.search(r"\%\s+SZS\s+status[^\n]*\n\%\s*\#?\s*SZS\soutput\sstart[^\n]*\n(?P<proof_text>(.|\n)*)\%\s*\#?\s*SZS\soutput\send", raw_proof_result)
        if match:
            return match.group(0)
        else:
            return raw_proof_result

class ResultHandler(BaseResultHandler):
    def get_used_axioms(self):
        raise NotImplementedError
