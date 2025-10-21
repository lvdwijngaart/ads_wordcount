# Pyright cannot interpret our auto-implementation of WordCountProxy since this is done at runtime.
# The comment below disables the error it would report otherwise.
# pyright: reportAbstractUsage=false

import os
import sys
import rpyc
from rpyc.utils.classic import obtain
import argparse
import time
import random

from common import WordCountProxy

# Envvars
RPYC_HOST = os.environ.get("RPYC_HOST", "localhost")
RPYC_PORT = int(os.environ.get("RPYC_PORT", "18861"))
MOCK_SEND_INTERVAL = int(os.environ.get("MOCK_SEND_INTERVAL", "1000"))


# List of keywords to choose from in mock mode. Currently tailored to `dune.txt`
keyword_list = [
    "paul",
    "duke",
    "fremen",
    "sand",
    "desert",
    "water",
    "spice",
    "leto",
    "atreides",
    "arrakis",
    "jessica",
    "reverend",
    "mentat",
    "harkonnen",
    "baron",
    "emperor",
    "sardaukar",
    "prophet",
    "stilgar",
    "sietch",
    "hawat",
    "duncan",
    "arrakeen",
    "sandworm",
]


def cli_parse():
    """
    Defines and parses command-line arguments
    """
    parser = argparse.ArgumentParser(prog="client.py")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run a mock client that repeatedly does random requests",
    )
    parser.add_argument(
        "-l", "--list-docs", action="store_true", help="Get a list of documents"
    )
    parser.add_argument("-d", "--document", help="ID of the document to search")
    parser.add_argument("-k", "--keyword", help="keyword to search for")

    return parser.parse_args()

def make_request_timed(svc: WordCountProxy, doc: str, keyword: str): 
    """
    Open a new rpyc connection for this single request, time it and close it
    """
    try: 
      conn = rpyc.connect(RPYC_HOST, RPYC_PORT)
      svc = WordCountProxy(conn.root)
    except Exception as e:
      print(f"Couldn't connect to server: {e}")
      return None, None
    
    t0 = time.perf_counter()
    try: 
      result = svc.count_words(doc, keyword)
    finally: 
      t1 = time.perf_counter()
      elapsed_ms = (t1 - t0) * 1000
      try: 
        conn.close()
      except Exception: 
        pass

    return result, elapsed_ms

def main():
    args = cli_parse()

    if args.list_docs:
      docs = get_docs()
      print("Available documents: ")
      for d in docs:
        print(d)
    elif args.mock:
      # Run in mock mode
      mock_loop()
    else:
      # single request (interactive)
      if not args.document:
        print("No document specified")
        exit(1)
      if not args.keyword:
        print("No keyword specified")
        exit(1)
      
      res, _ = make_request_timed(args.document, args.keyword)
      if res is None: 
        exit(1)
      print(f"Word count: {res['count']} (cached={res['cached']})")


def get_docs(): 
  # connect with server
  try:
    conn = rpyc.connect(RPYC_HOST, RPYC_PORT, config={"sync_request_timeout": 30})
    svc = WordCountProxy(conn.root)
    docs_remote = svc.list_docs()
    # materialize remote sequence locally while the connection is open
    try:
        docs = obtain(docs_remote)
    except Exception:
        docs = list(docs_remote)
    conn.close()
  except Exception as e:
    print(f"Couldn't connect to server: {e}")
    exit(1)

  return docs

def mock_loop():
    """
    Repeatedly send random requests to the server.
    """
    # get a list of documents to choose from
    # connect with server
    docs = get_docs()

    i = 0
    while True:
      i += 1
      # pick a random document + keyword, and send a request.
      doc = random.choice(docs)
      keyword = random.choice(keyword_list)
      result, elapsed_ms = make_request_timed(svc, doc, keyword)
      if result is None: 
        print("request failed")
      else: 
        print(f"request #{i+1}: elapsed={elapsed_ms:.3f} ms")
        print(result)

      time.sleep(MOCK_SEND_INTERVAL / 1000)


if __name__ == "__main__":
    main()
