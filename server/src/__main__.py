import os
import re
import hashlib
import rpyc
from rpyc.utils.server import ThreadedServer
import redis

from common import WordCountInterface, CountWordsResponse

# --- Config ---
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_TTL = int(os.environ.get("REDIS_TTL_SECONDS", "86400"))
RPYC_PORT = int(os.environ.get("RPYC_PORT", "18861"))
DOCS_DIR = os.environ.get("DOCS_DIR", "/data")

# Redis connection
rd = None

def read_document(doc_id: str) -> str:
    # Prevent path traversal
    if "/" in doc_id or "\\" in doc_id:
        raise ValueError("Invalid document ID")
    path = os.path.join(DOCS_DIR, doc_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Document {doc_id} not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def cache_key(doc: str, keyword: str) -> str:
    return f"wc:{doc}:{hash(keyword):x}"

@rpyc.service
class WordCountService(rpyc.Service, WordCountInterface):
    @rpyc.exposed
    def list_docs(self) -> list[str]:
        """ List available documents """
        return [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]

    @rpyc.exposed
    def count_words(self, doc: str, keyword: str) -> CountWordsResponse:
        """
        Returns {"count": int, "cached": bool}
        Caches by hashing the input text.
        """
        # matching is case insensitive, so we turn everthing lowercase to improve caching
        keyword = keyword.lower()
        key = cache_key(doc, keyword)

        cached_val = rd.get(key)
        if cached_val is not None:
            try:
                count = int(cached_val.decode("utf-8"))
                return {"doc": doc, "keyword": keyword, "count": count, "cached": True}
            except:
                # decoding/parsing error is treated as cache miss
                pass

        # cache miss: recompute
        text = read_document(doc)

        # Count occurrences. keyword is wrapped with word-boundary groups
        pattern = rf"\b{re.escape(keyword)}\b"
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))

        # write-back to cache
        rd.set(key, str(count), ex=REDIS_TTL)
        return {"doc": doc, "keyword": keyword, "count": count, "cached": False}

if __name__ == "__main__":
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} ...")
    rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    # verify connection
    try:
        rd.ping()
        print("Redis connection OK.")
    except Exception as e:
        print("Warning: could not ping Redis at startup:", e)

    print(f"Starting RPyC ThreadedServer on 0.0.0.0:{RPYC_PORT} ...")
    t = ThreadedServer(WordCountService, port=RPYC_PORT, protocol_config={"allow_public_attrs": True})
    t.start()
