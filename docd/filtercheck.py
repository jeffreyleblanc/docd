# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
A tool to check a directory for files containing phrases
"""

# Python
from pathlib import Path
# Local
from docd.utils.proc import proc


def run_filter_check(ctx, config, case_sensitive=False, files_only=False):
    ROOT_DIR = ctx.DOCS_DOCS_DIRPATH
    PHRASES = list(filter(len,config.check.filter_phrases.splitlines()))

    # Review the files
    no_matches = []
    for phrase in PHRASES:
        # Setup the grep flags
        flags = []
        if not case_sensitive:
            flags.append("--ignore-case")
        if files_only:
            flags.append("--color=never")
            flags.append("--files-with-matches")
        else:
            flags.append("--color=always")
            flags.append("--line-number")

        # Execute the command
        cmd = f"grep {' '.join(flags)} --recursive {phrase} {ROOT_DIR}"
        c,o,e = proc(cmd)

        # Process the output
        if c == 1:
            no_matches.append(phrase)
        elif c == 0:
            print(phrase)
            if files_only:
                for line in o.splitlines():
                    print(f"* {Path(line).relative_to(ROOT_DIR)}")
            else:
                o = o.replace(str(ROOT_DIR),"")
                print(o)
            print()
        else:
            raise Exception("Unknown error code")

    print(f"No matches:\n{no_matches}")

