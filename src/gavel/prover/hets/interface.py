import json
import tempfile

from gavel.settings import HETS_HOST
from gavel.settings import HETS_PORT
import requests as req

from urllib.parse import quote
from gavel.dialects.base.compiler import Compiler
from gavel.dialects.tptp.parser import TPTPParser
from gavel.logic.fol import Problem
from gavel.prover.base.interface import BaseProverInterface

class HetsCall:
    def __init__(self, paths):
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


class HetsProve(HetsCall, BaseProverInterface):
    def __init__(self, prover: BaseProverInterface):
        super(HetsProve, self).__init__(["prove"])
        self._internal_prover = prover

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

                    goals=[dict(node=node, reasonerConfiguration=dict(timeLimit=100, reasoner="Vampire"))],
                ),
            )
            if response.status_code == 200:
                jsn = json.loads(response.content.decode("utf-8"))[0]
                for goal in jsn["goals"]:
                    yield goal["prover_output"]
            else:
                raise Exception(response.content)








