import logging as log
from urllib.parse import quote

import requests as req

from gavel.settings import HETS_HOST
from gavel.settings import HETS_PORT


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
