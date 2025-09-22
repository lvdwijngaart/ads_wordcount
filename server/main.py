import os
import re
import hashlib
import rpyc
from rpyc.utils.server import ThreadedServer
import redis

# --- Config ---
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_TTL = int(os.environ.get("REDIS_TTL_SECONDS", "86400"))
RPYC_PORT = int(os.environ.get("RPYC_PORT", "18861"))
DOCS_DIR = os.environ.get("DOCS_DIR", "/data")

# Connect to Redis (single connection reused)
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

def cache_key(doc_id: str, text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"wc:{doc_id}:{h}"

class WordCountService(rpyc.Service):
    def exposed_list_docs(self):
        """ List available documents """
        return [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]

    def exposed_count_words(self, doc_id: str, keyword: str) -> dict:
        """
        Returns {"count": int, "cached": bool}
        Caches by hashing the input text.
        """
        key = cache_key(doc_id, keyword)
        cached_val = rd.get(key)
        if cached_val is not None:
            try:
                return {"doc": doc_id, "keyword": keyword, "count": int(cached_val.decode("utf-8")), "cached": True}
            except Exception:
                # Fall through to recompute if parsing fails
                pass
        text = read_document(doc_id)

        # Count occurrences
        pattern = rf"\b{re.escape(keyword)}\b"
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))

        # Cache as plain integer string with TTL
        rd.set(key, str(count), ex=REDIS_TTL)
        return {"doc": doc_id, "keyword": keyword, "count": count, "cached": False}

if __name__ == "__main__":
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} ...")
    rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    try:
        rd.ping()
        print("Redis connection OK.")
    except Exception as e:
        print("Warning: could not ping Redis at startup:", e)

    print(f"Starting RPyC ThreadedServer on 0.0.0.0:{RPYC_PORT} ...")
    t = ThreadedServer(WordCountService, port=RPYC_PORT, protocol_config={"allow_public_attrs": True})
    t.start()
