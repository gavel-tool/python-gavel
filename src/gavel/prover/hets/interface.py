import json
import tempfile
from urllib.parse import quote
from typing import Iterable


import requests as req

from gavel.dialects.tptp.dialect import TPTPDialect
from gavel.logic.fol import Problem, LogicElement, AnnotatedFormula
from gavel.prover.base.interface import BaseProverInterface
from gavel.config.settings import HETS_HOST
from gavel.config.settings import HETS_PORT
from gavel.prover.base.proof_structures import ProofGraph

class HetsCall:
    def __init__(self, paths, *args, **kwargs):
        super(HetsCall, self).__init__(*args, **kwargs)
        self.url = "http://" + HETS_HOST
        if HETS_PORT:
            self.url += ":" + str(HETS_PORT)
        self.url = "/".join([self.url] + paths)

    def get(self, path, *args, **kwargs):
        print(path)
        return self.__send(req.get, path, *args, **kwargs)

    def post(self, path, *args, data=None, **kwargs):
        return self.__send(req.post, path, *args, data=data, **kwargs)

    def __send(self, f, path, *args, **kwargs):
        return f(self.url + "/" + path, *args, **kwargs)

    @staticmethod
    def encode(path):
        return quote(path, safe="")


class HetsProve(BaseProverInterface, HetsCall):
    _prover_dialect_cls = TPTPDialect

    def __init__(self, prover_interface: BaseProverInterface, *args, **kwargs):
        super(HetsProve, self).__init__(["prove"])

    def _bootstrap_problem(self, problem: Problem):
        tf = tempfile.NamedTemporaryFile(mode="w+")
        problem_string = self.dialect.compile_problem(problem)
        tf.write(problem_string)
        tf.seek(0)
        return tf

    def _submit_problem(self, problem_instance, *args, **kwargs):
        node = str(problem_instance.name).split("/")[-1]
        iri = self.encode("file://" + str(problem_instance.name))
        response = self.post(
            iri,
            json=dict(
                format="json",
                goals=[
                    dict(
                        node=node,
                        reasonerConfiguration=dict(timeLimit=100, reasoner="Vampire"),
                    )
                ],
            ),
        )
        problem_instance.close()
        if response.status_code == 200:
            jsn = json.loads(response.content.decode("utf-8"))[0]
            for goal in jsn["goals"]:
                for line in goal["prover_output"].split("\n"):
                    yield line
        else:
            raise Exception(response.content)

    def _post_process_proof(self, raw_proof_result):
        for line in self.dialect.parse_many_expressions(raw_proof_result):
            yield line

    def _build_proof_graph(self, lines: Iterable[AnnotatedFormula], problem: Problem) -> ProofGraph:
        pg = ProofGraph(premises=problem.premises)
        d = {line.name: line for line in lines}


