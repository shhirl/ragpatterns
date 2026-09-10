"""Build the vector index from the ledger's text columns. Re-embeds only what changed.

  python3 service/ingest/build_index.py

Writes service/data/index.sqlite (git-ignored). Prints the numbers the method page publishes.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service.retrievers import vector

if __name__ == '__main__':
    print(json.dumps(vector.build(), indent=1))
