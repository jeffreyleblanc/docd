#! /usr/bin/env python3

from pathlib import Path
from docd.cli import run_cli

if __name__ == "__main__":

    # Determine if we are operating locally or from installed version,
    HERE = Path(__file__).parent
    GIT_DIR = HERE/".git/"
    if not GIT_DIR.is_dir():
        IN_DOCD_SOURCE_REPO = False
    else:
        IN_DOCD_SOURCE_REPO = True

    # Run the cli
    run_cli(IN_DOCD_SOURCE_REPO)
