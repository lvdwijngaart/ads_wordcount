# Pyright cannot interpret our auto-implementation of WordCountProxy since this is done at runtime.
# The comment below disables the error it would report otherwise.
# pyright: reportAbstractUsage=false

import os
import sys
import rpyc
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


def main():
    args = cli_parse()

    # connect with server
    try:
        conn = rpyc.connect(RPYC_HOST, RPYC_PORT)
        svc = WordCountProxy(conn.root)
    except Exception as e:
        print(f"Couldn't connect to server: {e}")
        exit(1)

    if args.list_docs:
        print("Available documents:")
        docs = svc.list_docs()
        for d in docs:
            print(d)
    elif args.mock:
        # Run in mock mode
        mock_loop(svc)
    else:
        # single request (interactive)
        if not args.document:
            print("No document specified")
            exit(1)
        if not args.keyword:
            print("No keyword specified")
            exit(1)

        res = svc.count_words(args.document, args.keyword)
        print(f"Word count: {res['count']} (cached={res['cached']})")


def mock_loop(svc: WordCountProxy):
    """
    Repeatedly send random requests to the server.
    """
    # get a list of documents to choose from
    docs = svc.list_docs()

    while 1:
        # pick a random document + keyword, and send a request.
        doc = random.choice(docs)
        keyword = random.choice(keyword_list)
        result = svc.count_words(doc, keyword)

        print(result)
        time.sleep(MOCK_SEND_INTERVAL / 1000)


if __name__ == "__main__":
    main()
