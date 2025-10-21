# Pyright cannot interpret our auto-implementation of WordCountProxy since this is done at runtime.
# The comment below disables the error it would report otherwise.
#pyright: reportAbstractUsage=false

import os
import sys
import rpyc
import argparse
import time
import random
import matplotlib.pyplot as plt
import numpy as np

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

y1 = np.array([])

def cli_parse():
    """
    Defines and parses command-line arguments
    """
    parser = argparse.ArgumentParser(
        prog='client.py'
    )
    parser.add_argument('--mock', action='store_true', help='Run a mock client that repeatedly does random requests')
    parser.add_argument('-l', '--list-docs', action='store_true', help='Get a list of documents')
    parser.add_argument('-d', '--document', help='ID of the document to search')
    parser.add_argument('-k', '--keyword', help='keyword to search for')

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
        # mock_loop(svc)
        y1 = mock_graph(svc)
        make_graph(svc, y1)
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

def mock_graph(svc: WordCountProxy):
    """
    Repeatedly send requests to the server for a certain word.
    """
    # get a list of documents to choose from
    docs = svc.list_docs()
    i=0
    list = []
    while i<25:
        # pick a random document + keyword, and send a request.
        doc = random.choice(docs)
        if i<5:
            keyword = "sand"
            start_time = time.perf_counter()
            result = svc.count_words(doc, keyword)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"request #{i+1}: elapsed={elapsed_time:.3f} ms")
            print(result)
            list.append([elapsed_time])
            time.sleep(MOCK_SEND_INTERVAL / 1000)
        elif i>=5 and i<10:
            keyword = "sandworm"
            start_time = time.perf_counter()
            result = svc.count_words(doc, keyword)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"request #{i+1}: elapsed={elapsed_time:.3f} ms")
            print(result)
            list.append([elapsed_time])
            time.sleep(MOCK_SEND_INTERVAL / 1000)
        elif i>=10 and i<15:
            keyword = "water"
            start_time = time.perf_counter()
            result = svc.count_words(doc, keyword)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"request #{i+1}: elapsed={elapsed_time:.3f} ms")
            print(result)
            list.append([elapsed_time])
            time.sleep(MOCK_SEND_INTERVAL / 1000)
        elif i>=15 and i<20:
            keyword = "arrakis"
            start_time = time.perf_counter()
            result = svc.count_words(doc, keyword)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"request #{i+1}: elapsed={elapsed_time:.3f} ms")
            print(result)
            list.append([elapsed_time])
            time.sleep(MOCK_SEND_INTERVAL / 1000)
        elif i>=20 and i<25:
            keyword = "paul"
            start_time = time.perf_counter()
            result = svc.count_words(doc, keyword)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"request #{i+1}: elapsed={elapsed_time:.3f} ms")
            print(result)
            list.append([elapsed_time])
            time.sleep(MOCK_SEND_INTERVAL / 1000)
        i+=1

    list = np.array(list)
    return list
def make_graph(svc: WordCountProxy, y1: np.ndarray):
    y = np.asarray(y1, dtype=float).reshape(-1)
    x = np.arange(1, len(y1) + 1)
    THRESHOLD_MS = 10.0
    n = y.size
    group_size = n // 5           # first half: "sand", second half: "sandworm", third half: "water"
    gap = 0.75                     # visual gap between groups

    # x-positions: [0..4] for "sand", [6..10] for "sandworm", [12..16] for "water" , [18..22] for "arrakis", [24..28] for "paul" (with a gap of 0.75)
    x_sand = np.arange(group_size)
    x_sandworm = np.arange(group_size) + group_size + gap
    x_water = np.arange(group_size) + 2 * group_size + 2 * gap
    x_arrakis = np.arange(group_size) + 3 * group_size + 3 * gap
    x_paul = np.arange(group_size) + 4 * group_size + 4 * gap
    x_all = np.concatenate([x_sand, x_sandworm, x_water, x_arrakis, x_paul])

    # Colors: >10 ms gets a different color
    colors = ["tab:red" if v > THRESHOLD_MS else "tab:blue" for v in y]

    plt.figure(figsize=(10, 4))
    plt.bar(x_all, y, color=colors, edgecolor="black")

    # Group labels at group centers
    centers = [x_sand.mean(), x_sandworm.mean(), x_water.mean(), x_arrakis.mean(), x_paul.mean()]
    labels = ["'sand' \n(count = 302)", "'sandworm' \n(count = 12)", "'water' \n(count = 374)", "'arrakis' \n(count = 329)", "'paul' \n(count = 1722)"]
    plt.xticks(centers, labels)
    plt.xlabel("Requested words (x5)")
    plt.ylabel("Latency (ms)")
    plt.title("Request latency over time (grouped bar chart)")
    plt.grid(axis="y", alpha=0.3)
    plt.xlim(min(x_all) - 0.5, max(x_all) + 0.5)

    # Legend (color meaning)
    from matplotlib.patches import Patch
    legend_patches = [
        Patch(color="tab:blue", label=f"Cached request"),
        Patch(color="tab:red", label=f"Non-cached request"),
    ]
    plt.legend(handles=legend_patches, loc="upper right")

    # Save to file (headless container)
    out_path = "latency_plot.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {out_path}")
    while 1:
        time.sleep(1)

if __name__ == "__main__":
    main()
