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

@dataclass
class DocdRunContext:
    IN_DOCD_SOURCE_REPO: bool = False
    SUPPORT_RESOURCES_DIRPATH: Path = None
    # Docs info
    DOCS_REPO_DIRPATH: Path = None
    DOCS_CONFIG_FILEPATH: Path = None
    DOCS_DOCS_DIRPATH: Path = None
    DOCS_DIST_DIRPATH: Path = None

DEFAULT_PORT = 8001


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

        c,o,e = proc("make build",cwd=SPA_SRC_DIR)
        print(c,o,e)

        dt = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        stamp = f"/* built: {dt} */"

        # In future we could get the md5sum within python
        for fp in DIST_SRC_DIR.iterdir():
            ## print("=>",fp)
            if fp.stem.startswith("index") and fp.suffix == ".css":
                print("css: ",fp)
                c,o,e = proc(f"md5sum {fp}")
                print("~~>",o[:12])
                moved_file = SUPPORT_STATIC_DIR/f"docd-core-{o[:12]}.css"
                fp.rename(moved_file)

                with moved_file.open("a") as fp:
                    fp.write(stamp)

            elif fp.stem.startswith("index") and fp.suffix == ".js":
                print("js: ",fp)
                c,o,e = proc(f"md5sum {fp}")
                print("~~>",o[:12])
                moved_file = SUPPORT_STATIC_DIR/f"docd-core-{o[:12]}.js"
                fp.rename(moved_file)

                with moved_file.open("a") as fp:
                    fp.write(stamp)

            else:
                print("map",fp)
                fp.rename(SUPPORT_STATIC_DIR/fp.name)

        return

        # Make and clean the _dist directory
        self.DIST_PATH.mkdir(exist_ok=True,parents=True)
        glob_delete(self.DIST_PATH,"dist.compiled*")

        # Build the src
        c,o,e = proc("make build-web",cwd=self.SRC_PATH)
        print(c,o,e)

        exit()

        # Calculate hash and move compiled js into _dist
        c,o,e = proc("md5sum src/dist.compiled.js")
        fhash = o[:8]
        new_path = self.DIST_PATH/f"dist.compiled.{fhash}.js"
        Path("src/dist.compiled.js").replace(new_path)

        # Append the build time to the js dist
        dt = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        stamp = f"/* built: {dt} */"
        with new_path.open("a") as fp:
            fp.write(stamp)

        exit()


if __name__ == "__main__":
    main()
