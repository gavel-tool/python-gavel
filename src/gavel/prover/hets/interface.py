import json
import tempfile
from typing import Iterable
from urllib.parse import quote

import requests as req

from gavel.config.settings import HETS_HOST
from gavel.config.settings import HETS_PORT
from gavel.dialects.tptp.dialect import TPTPDialect
from gavel.logic.logic import LogicElement
from gavel.logic.problem import AnnotatedFormula
from gavel.logic.problem import Problem
from gavel.logic.proof import Proof
from gavel.prover.base.interface import BaseProverInterface


class HetsEngine:

    def __init__(self, url, port=80):
        self.url = url
        self.port = port

    @property
    def connection_string(self, path=None):
        return "http://{url}:{port}".format(
            url=self.url,
            port=self.port
        )


def connection_wrapper(f):
    def inner(self, paths, **kwargs):
        s = self.engine.connection_string
        if paths is not None:
            s += "/" + "/".join(paths)
        result = f(self, s, **kwargs)
        assert 200 <= result.status_code < 300
        return result.content
    return inner


class HetsSession:
    def __init__(self, engine, *args, **kwargs):
        super(HetsSession, self).__init__(*args, **kwargs)
        self.engine = engine
        self.folder = self.get(["folder"])

    @connection_wrapper
    def get(self, *args, **kwargs):
        return req.get(*args, **kwargs)

    @connection_wrapper
    def post(self, *args, **kwargs):
        return req.post(*args, **kwargs)

    @staticmethod
    def encode(path):
        return quote(path, safe="")

    def upload(self, fp):
        with open(fp) as fil:
            self.post(["uploadFile", self.folder], data=fil.read())
            return quote("/".join([self.folder, fp]), safe="")


class HetsProve(BaseProverInterface):
    _prover_dialect_cls = TPTPDialect

    def __init__(self, prover_interface: BaseProverInterface, session, *args, **kwargs):
        super(HetsProve, self).__init__()
        self.session = session

    def _bootstrap_problem(self, problem: Problem):
        with tempfile.NamedTemporaryFile(mode="w+") as tf:
            problem_string = self.dialect.compile_problem(problem)
            tf.write(problem_string)
            return self.session.upload(tf.name)

    def _submit_problem(self, problem_instance, *args, **kwargs):
        response = self.session.post( "/".join("prove", problem_instance),
            json=dict(
                format="json",
                goals=[
                    dict(
                        node=problem_instance,
                        reasonerConfiguration=dict(timeLimit=100, reasoner="Vampire"),
                    )
                ],
            ),
        )
        if response.status_code == 200:
            jsn = json.loads(response.content.decode("utf-8"))[0]
            assert "goals" in jsn
            goals = jsn["goals"]
            assert len(goals) == 1
            return goals[0]["prover_output"]
        else:
            raise Exception(response.content)

    def _post_process_proof(self, raw_proof_result):
        return raw_proof_result
