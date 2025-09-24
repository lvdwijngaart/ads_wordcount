from abc import ABC, abstractmethod, update_abstractmethods
import time
from typing import TypedDict
import inspect

class CountWordsResponse(TypedDict):
    doc: str
    keyword: str
    count: int
    cached: bool

class WordCountInterface(ABC):
    @abstractmethod
    def count_words(self, doc: str, keyword: str) -> CountWordsResponse:
        pass

    @abstractmethod
    def list_docs(self) -> list[str]:
        pass

# Auto generated RPC proxy

def build_proxy_fn(fname: str):
    def inner(self, *args, **kwargs):
        fn = getattr(self.conn, fname)
        t1 = time.process_time_ns() / 1000000
        value = fn(*args, **kwargs)
        t2 = time.process_time_ns() / 1000000
        diff = t2 - t1
        print(f"[RPYC] '{fname}' took {diff:0.2} ms")
        return value
    return inner

class WordCountProxy(WordCountInterface):
    def __init__(self, conn):
        self.conn = conn

for fn in WordCountInterface.__abstractmethods__:
    setattr(WordCountProxy, fn, build_proxy_fn(fn))

update_abstractmethods(WordCountProxy)
