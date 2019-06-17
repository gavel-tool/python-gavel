import json
import tempfile

from gavel.dialects.base.compiler import Compiler
from gavel.dialects.tptp.tptpparser import TPTPParser
from gavel.logic.fol import Problem
from gavel.prover.base.proof import ProverInterface
from gavel.prover.hets.interface import HetsCall


class HetsProve(HetsCall, ProverInterface):
    def __init__(self):
        super(HetsProve, self).__init__(["prove"])

    def prove(self, problem: Problem, compiler: Compiler, *args, **kwargs):
        with tempfile.NamedTemporaryFile(mode="w+") as tf:
            node = str(tf.name).split("/")[-1]
            iri = self.encode("file://" + str(tf.name))
            problem_string = compiler.visit_problem(problem)
            tf.write(problem_string)
            tf.seek(0)
            response = self.post(
                iri,
                json=dict(
                    format="json",
                    goals=[dict(node=node, reasonerConfiguration=dict(timeLimit=100))],
                ),
            )
            if response.status_code == 200:
                self.get_used_axioms(json.loads(response.content.decode("utf-8"))[0])
            else:
                raise Exception(response.content)

    def get_used_axioms(self, jsn):
        parser = TPTPParser()
        for goal in jsn["goals"]:
            result = parser.load_expressions(goal["prover_output"].split("\n"))
            for formula in result:
                print(formula.annotation)
