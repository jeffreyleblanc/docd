#! /usr/bin/env python3

# Python
from pathlib import Path
import json
# Lunr
from lunr import lunr


def create_markdown_docs(ROOT):
    DOCS = []
    for fpath in sorted(ROOT.glob("**/*.md")):
        ref = fpath.relative_to(ROOT)
        entry = {
            "path": ref,
            "title": ref,
            "body": ""
        }
        with fpath.open("r") as fp:
            entry["body"] = fp.read()
        DOCS.append(entry)

    return DOCS

def main():
    print("main")

    REPO_ROOT = Path("/home/jleblanc/code/DOCS/")

    # Create the documents
    SEARCH_ROOT = REPO_ROOT/"docs/"
    DOCS = create_markdown_docs(SEARCH_ROOT)

    # Generate the indexer
    indexer = lunr(ref="path",fields=("title","body"),documents=DOCS)

    # Output the serialized index
    serialized_index = indexer.serialize()
    OUTPUT = REPO_ROOT/"_dist/_search"
    OUTPUT.mkdir(exist_ok=True)
    with (OUTPUT/"serialized-index.json").open("w") as fp:
        json.dump(serialized_index,fp,indent=None)

    # # Interact with it
    # import code
    # code.interact(local=locals())


if __name__ == "__main__":
    main()
