import os
import sys
import rpyc

# When running via docker compose, the server is reachable by its service name "server".
RPYC_HOST = os.environ.get("RPYC_HOST", "server")
RPYC_PORT = int(os.environ.get("RPYC_PORT", "18861"))

def main():
    if len(sys.argv) < 3:
        print("Usage: python client.py <text to count>")
        print('Example: python client.py "Hello world hello"')
        sys.exit(1)

    conn = rpyc.connect(RPYC_HOST, RPYC_PORT)
    svc = conn.root

    doc_id, keyword = sys.argv[1], sys.argv[2]
    print("Docs available", svc.list_docs())
    res = svc.count_words(doc_id, keyword)
    print(f"Text: {keyword}")
    print(f"Word count: {res['count']} (cached={res['cached']})")

if __name__ == "__main__":
    main()
