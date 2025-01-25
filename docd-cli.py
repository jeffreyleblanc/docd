#! /usr/bin/env python3

from pathlib import Path
from docd.cli import run_cli

if __name__ == "__main__":

    # Determine if we are operating locally or from installed version,
    # and then set support paths accordingly
    HERE = Path(__file__).parent
    if HERE == Path("/usr/local/bin"):
        IN_DOCD_SOURCE_REPO = False
    else:
        IN_DOCD_SOURCE_REPO = True

    run_cli(IN_DOCD_SOURCE_REPO)
