import os
import sys
import rpyc
import argparse
import time
import random

RPYC_HOST = os.environ.get("RPYC_HOST", "localhost")
RPYC_PORT = int(os.environ.get("RPYC_PORT", "18861"))
MOCK_SEND_INTERVAL = int(os.environ.get("MOCK_SEND_INTERVAL", "1000"))

keyword_list = [
    "hello",
    "hi",
    "world",
]

document_list = [
    "doc1.txt"
]


def main():
    parser = argparse.ArgumentParser(
        prog='client.py'
    )
    parser.add_argument('--mock', action='store_true', help='Run a mock client that repeatedly does random requests')
    parser.add_argument('-l', '--list-docs', action='store_true', help='Get a list of documents')
    parser.add_argument('-d', '--document', help='ID of the document to search')
    parser.add_argument('-k', '--keyword', help='keyword to search for')

    args = parser.parse_args()

    try:
        conn = rpyc.connect(RPYC_HOST, RPYC_PORT)
        conn.root
    except Exception as e:
        print(f"Couldn't connect to server: {e}")
        exit(1)

    if args.list_docs:
        print("Available documents:")
        for d in conn.root.list_docs():
            print(d)
    elif args.mock:
        print("Running mock")
        mock_loop(conn.root)
    else:
        doc, keyword = args.document, args.keyword

        if not doc:
            print("No document specified")
            exit(1)
        if not keyword:
            print("No keyword specified")
            exit(1)

        res = conn.root.count_words(doc, keyword)
        print(f"Word count: {res['count']} (cached={res['cached']})")

def mock_loop(svc):
    while 1:
        doc = random.choice(document_list)
        keyword = random.choice(keyword_list)
        result = svc.count_words(doc, keyword)
        print(result)
        time.sleep(MOCK_SEND_INTERVAL / 1000)

if __name__ == "__main__":
    main()
