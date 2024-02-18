#! /usr/bin/env python3

# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import argparse
from pathlib import Path
from dataclasses import dataclass
import toml
import json
import datetime
from docd.utils.proc import proc
from docd.utils.obj import DictObj
from docd.utils.filetools import file_md5, file_sha256

@dataclass
class DocdRunContext:
    IN_DOCD_SOURCE_REPO: bool = False
    SUPPORT_RESOURCES_DIRPATH: Path = None
    # Docs info
    DOCS_REPO_DIRPATH: Path = None
    DOCS_CONFIG_FILEPATH: Path = None
    DOCS_DOCS_DIRPATH: Path = None
    DOCS_DIST_DIRPATH: Path = None


def build_web(add_timestamp=False):
    # In future we could get the md5sum within python

    # Determine paths
    HERE = Path(__file__).parent
    SPA_SRC_DIR = HERE/"spa-src"
    DIST_SRC_DIR = SPA_SRC_DIR/"dist/static"
    SUPPORT_DIR = HERE/"support"
    SUPPORT_STATIC_DIR = SUPPORT_DIR/"static"

    # clear the support/static
    SUPPORT_STATIC_DIR.mkdir(exist_ok=True)
    for fp in SUPPORT_STATIC_DIR.iterdir():
        if fp.is_dir():
            shutil.rmtree(fp)
        else:
            fp.unlink()

    # Build the source
    """
    `make build` will produce:
    docd$ ls -1 spa-src/dist/static/
        index-JSHASH.js
        index-JSHASH.js.map
        index-CSSHASH.css
    where:
        JSHASH =  first 8 char of the sha256 of index-JSHASH.js
        CSSHASH = first 8 char of the sha256 of index-CSSHASH.css
    """
    c,o,e = proc("make build",cwd=SPA_SRC_DIR)
    print(c,o,e)
    assert c == 0

    # Iterate over the built files
    dt = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    INSTALLED_FILES = {}
    for fp in DIST_SRC_DIR.iterdir():
        # Get the stem and suffix
        fstem = fp.stem
        fsuffix = "".join(fp.suffixes)

        if fstem.startswith("index") and fsuffix == ".css":
            # Make a new name for the file
            sha256 = file_sha256(fp)
            CSS_NAME = f"docd-core-{sha256[:8]}.css"
            INSTALLED_FILES["docd_css_file"] = f"static/{CSS_NAME}"

            # Move the file and append timestamp
            moved_file = SUPPORT_STATIC_DIR/CSS_NAME
            fp.rename(moved_file)
            if add_timestamp:
                with moved_file.open("a") as fp:
                    fp.write(stamp)

        elif fstem.startswith("index") and fsuffix == ".js":
            # Make a new name for the file
            sha256 = file_sha256(fp)
            JS_NAME = f"docd-core-{sha256[:8]}.js"
            INSTALLED_FILES["docd_js_file"] = f"static/{JS_NAME}"

            # Move the file and append timestamp
            moved_file = SUPPORT_STATIC_DIR/JS_NAME
            fp.rename(moved_file)
            if add_timestamp:
                with moved_file.open("a") as fp:
                    fp.write(stamp)

        elif fsuffix == ".js.map":
            INSTALLED_FILES["docd_js_map"] = f"static/{fp.name}"
            fp.rename(SUPPORT_STATIC_DIR/fp.name)

        else:
            raise Exception("UNKNOWN FILE!",fp)

    # Make datestamp and storage for the file names
    INSTALLED_FILES["built"] = f"{dt}"

    # Write out the helper
    HELPER_PATH = SUPPORT_DIR/"static-info.json"
    with HELPER_PATH.open("w") as f:
        f.write(json.dumps(INSTALLED_FILES,indent=4))


def main():
    __VERSION__ = "0.0.1"

    #-- Make the argparser -----------------------------------------------------------#

    # Main Parser
    parser = argparse.ArgumentParser(description="docd: For building awesome docs.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__VERSION__}")
    # Create subparsers
    subparsers = parser.add_subparsers(help="sub-command help",dest="main_command")
    # Commands
    subp_wbuild = subparsers.add_parser("build-web",help="Build the web")


    #-- Process args and context-----------------------------------------------------------#

    # Parse the args
    args = parser.parse_args()
    if args.main_command is None:
        # Can also `parser.print_usage()`
        parser.print_help()
        exit(1)

    # Make Context Object
    ctx = DocdRunContext()

    # Determine if we are operating locally or from installed version,
    # and then set support paths accordingly
    _here = Path(__file__).parent
    if _here == Path("/usr/local/bin"):
        ctx.IN_DOCD_SOURCE_REPO = False
        ctx.SUPPORT_RESOURCES_DIRPATH = Path("/usr/local/lib/docd/support/")
    else:
        ctx.IN_DOCD_SOURCE_REPO = True
        ctx.SUPPORT_RESOURCES_DIRPATH = _here/"support/"
    assert ctx.SUPPORT_RESOURCES_DIRPATH.is_dir()

     #-- Internal docd Tools -----------------------------------------------------------#

    if args.main_command == "build-web":
        build_web()


if __name__ == "__main__":
    main()
