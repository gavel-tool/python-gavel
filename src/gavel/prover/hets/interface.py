import json
import tempfile
from typing import Iterable
from urllib.parse import quote

import requests as req

from gavel.config.settings import HETS_HOST
from gavel.config.settings import HETS_PORT
from gavel.dialects.tptp.dialect import TPTPProblemDialect
from gavel.logic.logic import LogicElement
from gavel.logic.problem import AnnotatedFormula
from gavel.logic.problem import Problem
from gavel.logic.solution import Proof
from gavel.prover.base.interface import BaseProverInterface
from gavel.config import settings


class HetsEngine:
    def __init__(self, url=None, port=None):
        if url is None:
            self.url = settings.HETS_HOST
        else:
            self.url = url
        if port is None:
            self.port = settings.HETS_PORT
        else:
            self.port = port

    @property
    def connection_string(self, path=None):
        return "http://{url}:{port}".format(url=self.url, port=self.port)


def connection_wrapper(f):
    def inner(self, paths, **kwargs):
        s = self.engine.connection_string
        if paths is not None:
            s += "/" + "/".join(paths)
        result = f(self, s, **kwargs)
        assert 200 <= result.status_code < 300, result.content
        return result.content

    return inner


class HetsSession:
    def __init__(self, engine, *args, **kwargs):
        super(HetsSession, self).__init__(*args, **kwargs)
        self.engine = engine
        self.http_session = req.Session()
        self.folder = self.get(["folder"]).decode("utf-8")[len("/tmp/") :]
        self.files = []

    def add_file(self, content):
        f_name = "f%d" % len(self.files)
        self.files.append(f_name)
        return f_name

    @connection_wrapper
    def get(self, *args, **kwargs):
        return self.http_session.get(*args, timeout=86400, **kwargs)

    @connection_wrapper
    def post(self, *args, **kwargs):
        return self.http_session.post(*args, timeout=86400, **kwargs)

    @staticmethod
    def encode(path):
        return quote(path, safe="")

    def upload(self, name, content):
        enc_folder = quote(self.folder, safe="")
        enc_file = quote(name, safe="")
        self.post(["uploadFile", enc_folder, enc_file], data=content)
        return enc_folder, enc_file


class HetsProve(BaseProverInterface):
    def __init__(
        self,
        prover_interface: BaseProverInterface,
        session: HetsSession,
        *args,
        **kwargs
    ):
        self._prover_dialect_cls = prover_interface._prover_dialect_cls
        super(HetsProve, self).__init__()
        self.session = session

    def _bootstrap_problem(self, problem: Problem):
        problem_string = "\n".join(self.dialect.compile(l) for l in problem.premises)
        problem_string += self.dialect.compile(problem.conjecture)
        name = self.session.add_file(problem_string)
        return self.session.upload(name, problem_string), problem

    def _submit_problem(self, problem_instance, *args, **kwargs):
        (folder_name, file_name), problem = problem_instance
        response = self.session.post(
            ["prove", "%2F".join(["", "tmp", folder_name, file_name])],
            json=dict(
                format="json",
                goals=[
                    dict(
                        node="f0",
                        reasonerConfiguration=dict(timeLimit=100, reasoner="EProver"),
                        useTheorems=False,
                    )
                ],
                premiseSelection=dict(
                    kind="manual", manualPremises=[a.name for a in problem.premises]
                ),
            ),
        )
        jsn = json.loads(response.decode("utf-8"))["prover_output"][0]
        assert "goals" in jsn
        goals = jsn["goals"]
        assert len(goals) == 1
        return goals[0]["prover_output"]

    def _post_process_proof(self, raw_proof_result):
        return raw_proof_result
