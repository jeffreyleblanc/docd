# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
A tool to check a directory for files containing phrases
"""

# Python
from pathlib import Path
# Things
import toml
# Local
from docd.utils.proc import proc

def main_run(ctx, config):
    run_check(ctx.DOCS_DOCS_DIRPATH, config)

def run_check(ROOT_DIR, config):
    PHRASES = list(filter(len,config.check.filter_phrases.splitlines()))

    # Review the files
    no_matches = []
    for phrase in PHRASES:
        c,o,e = proc(f"grep --color=never -i -l -r -n {phrase} {ROOT_DIR}")
        if c == 1:
            no_matches.append(phrase)
        elif c == 0:
            print(phrase)
            for line in o.splitlines():
                print(f"* {Path(line).relative_to(ROOT_DIR)}")
            print()
        else:
            raise Exception("Unknown error code")

    print(f"No matches:\n{no_matches}")

