from abc import ABC, abstractmethod, update_abstractmethods
from sys import stderr
import time
from typing import TypedDict
import inspect

class CountWordsResponse(TypedDict):
    doc: str
    keyword: str
    count: int
    cached: bool

class WordCountInterface(ABC):
    """
    Interface for the word count server.

    `WordCountProxy` auto-implements this interface at runtime.
    """
    @abstractmethod
    def count_words(self, doc: str, keyword: str) -> CountWordsResponse:
        """
        Counts the number of occurences of `keyword` in document `doc`.
        """
        pass

    @abstractmethod
    def list_docs(self) -> list[str]:
        """
        Get a list of available documents.
        """
        pass

# --- Proxy auto-implementation:
# A Proxy is an implementation of an RPC interface by simply performing the corresponding RPC
# calls. Since implementation is trivial we can auto-generate this with some python magic.

# Function generator for proxy methods. Takes the function name and returns a function
# that performs the corresponding RPC call.
def build_proxy_fn(fname: str):
    def inner(self, *args, **kwargs):
        # Get the corresponding rpyc call
        fn = getattr(self.conn, fname)
        # Send request and measure latency
        t1 = time.process_time_ns() / 1000000
        value = fn(*args, **kwargs)
        t2 = time.process_time_ns() / 1000000
        diff = t2 - t1
        print(f"[RPYC] '{fname}' took {diff:0.2} ms", file=stderr)
        return value
    return inner

class WordCountProxy(WordCountInterface):
    def __init__(self, conn):
        self.conn = conn

# Auto-implementation
for fn in WordCountInterface.__abstractmethods__:
    setattr(WordCountProxy, fn, build_proxy_fn(fn))

# Abstract methods are runtime checked, this makes sure we can call the methods we auto-implemented
# during runtime. LSPs like PyRight might still complain about unimplemented methods, this can be ignored.
update_abstractmethods(WordCountProxy)
