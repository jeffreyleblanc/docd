#! /usr/bin/env python3

# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import argparse
from pathlib import Path
from dataclasses import dataclass
import toml
import json
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

def load_config(config_fpath):
    # Load the config
    config = DictObj(toml.load(config_fpath))

    # Look for config dictionary
    if "source" not in config:
        config.source = DictObj({})
    if "max_depth" not in config.source:
        config.source.max_depth = 2
    if not isinstance(config.source.max_depth,int):
        raise Exception("config.config.max_depth must be an integer")
    if "file_types" not in config.source:
        config.file_types = {
            ".md":"markdown",
            ".py":"python",
            ".txt":"",
            ".html":"html",
            ".sh":"bash",
            ".bash":"bash",
            ".vue":"html",
            ".js":"javascript",
            ".css":"css",
            ".conf":"bash",
            "":""
        }

    # Make sure we have the 'site' attributes
    for k in ( "site.title","site.author","site.name","site.footer" ):
        if config.get_path(k) is None:
            raise Exception(f"docd.toml missing `{k}`")
    if "home_addr" not in config.site:
        config.site.home_addr = ""

    # Check on 'remote' attributes
    if "remote" not in config:
        config.remote = None
    else:
        for k in ( "remote.user","remote.addr","remote.path" ):
            if config.get_path(k) is None:
                raise Exception(f"docd.toml missing `{k}`")

    # Check on 'check' attributes
    if "check" not in config:
        config.check = DictObj({})
    if "filter_phrases" not in config.check:
        config.check.filter_phrases = ""

    return config


if __name__ == "__main__":
    __VERSION__ = "0.0.4"

    #-- Make the argparser -----------------------------------------------------------#

    # Main Parser
    parser = argparse.ArgumentParser(description="docd: For building awesome docs.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__VERSION__}")
    parser.add_argument("-R","--repo-directory",help="Root document repo directory. Defaults to cwd.",default=None)

    # Create subparsers
    subparsers = parser.add_subparsers(help="sub-command help",dest="main_command")

    # builders
    subp_build = subparsers.add_parser("build", help="Build the complete docd site")
    subp_spa = subparsers.add_parser("spa", help="Make the docd spa scaffold")
    subp_publish = subparsers.add_parser("publish", help="Convert the source docs to html")
    subp_publish.add_argument("-f","--filepath",default=None)
    subp_clean = subparsers.add_parser("clean", help="Clean out the docd site")

    # Push
    subp_push = subparsers.add_parser("push", help="Push docs to a remote")

    # Check
    subp_check = subparsers.add_parser("check", help="Check docs for filter phrases")

    # Helper Methods
    subp_info = subparsers.add_parser("info", help="Print info on the repo config")

    # Helper Methods
    subp_devserver = subparsers.add_parser("devserver", help="Run the new server")

    #-- Process args -----------------------------------------------------------#

    args = parser.parse_args()
    if args.main_command is None:
        # Can also `parser.print_usage()`
        parser.print_help()
        exit(1)

    #-- Generate Context -----------------------------------------------------------#

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

    # Determine the doc repo paths
    _repo = Path(args.repo_directory) if args.repo_directory is not None else Path.cwd()
    ctx.DOCS_REPO_DIRPATH = _repo
    assert ctx.DOCS_REPO_DIRPATH.is_dir()
    ctx.DOCS_CONFIG_FILEPATH = _repo/"docd.toml"
    assert ctx.DOCS_CONFIG_FILEPATH.is_file()
    ctx.DOCS_DOCS_DIRPATH = _repo/"docs/"
    assert ctx.DOCS_DOCS_DIRPATH.is_dir()
    ctx.DOCS_DIST_DIRPATH = _repo/"_dist/"

    # Load the config
    config = load_config(ctx.DOCS_CONFIG_FILEPATH)

    #-- Execute the Commands -----------------------------------------------------------#

    match args.main_command:
        case "info":
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            print("# args:")
            pp.pprint(args)
            print("\n# ctx:")
            pp.pprint(ctx)
            print("\n# config:")
            print(json.dumps(config.to_dict(),indent=4))

        # case ("build"|"spa"|"publish"):
        #     from docd.publisher import Publisher
        #     pub = Publisher(ctx,config)
        #     if args.main_command in ("build","spa"):
        #         pub.build_spa()
        #     if args.main_command in ("build","publish"):
        #         pub.build_docs()

        case "build":
            from docd.publisher import Publisher
            pub = Publisher(ctx,config)
            pub.build_docs()
            # if args.main_command in ("build","spa"):
            #     pub.build_spa()
            # if args.main_command in ("build","publish"):
            #     pub.build_docs()

        case "clean":
            import shutil
            assert ctx.DOCS_DIST_DIRPATH.is_dir()
            for fp in ctx.DOCS_DIST_DIRPATH.iterdir():
                if fp.is_dir():
                    shutil.rmtree(fp)
                else:
                    fp.unlink()

        case "check":
            import docd.cmd_check as CHECK
            CHECK.main_run(ctx,config)

        case "push":
            # Pull out info
            remote = config.remote
            if remote is None:
                raise Exception("No remote is defined.")
            user = remote.user
            addr = remote.addr
            remote_path = remote.path

            # Assemble paths
            src = f"{ctx.DOCS_DIST_DIRPATH}/."
            dst = remote_path
            if dst.endswith("/."):
                pass
            elif dst.endswith("/"):
                dst += "."
            else:
                dst += "/."
            assert src.endswith("/.") and not src.endswith("//.")
            assert dst.endswith("/.") and not dst.endswith("//.")

            # Make the rsync command
            cmd = f"rsync -avz --delete {src} {user}@{addr}:{dst}"
            c,o,e = proc(cmd)
            print(c,o,e)

        case "devserver":

            import asyncio
            from docd.devserver import DocdDevServer

            # Load the new spa page template
            SPA_TEMPLATE_PATH = Path("support/templates/spa.html")
            with SPA_TEMPLATE_PATH.open("r") as fp:
                SPA_TEMPLATE = fp.read()

            # Make a temporary config for now
            # Leave off the css and js as those will be dynamically added
            SPA_CONFIG = {
                "__TITLE__":    "Temp TITLE",
                "__AUTHOR__":   "Alice and Bob",
                "__NAME__" :    "Sample Docs",
                "__FOOTER__":   "Copyright Me",
                "__HOME_URL__": "/",
                # "__CSS_FILE__": "/static/main.css",
                # "__JS_FILE__":  "/static/main.js"
            }
            for k,v in SPA_CONFIG.items():
                SPA_TEMPLATE = SPA_TEMPLATE.replace(k,v)

            # Set the static directory as where vite builds to
            STATIC_DIR = Path("spa-src/dist/static")

            # Set the file paths
            FILE_PATHS = dict(
                _resources =     ctx.DOCS_DIST_DIRPATH/"_resources",
                # media =  ctx.DOCS_DIST_DIRPATH/"_media/",
                # search = ctx.DOCS_DIST_DIRPATH/"_search/",
                # static = ctx.DOCS_DIST_DIRPATH/"static/"
                static = STATIC_DIR
            )

            async def run_server():
                PORT = 8100
                ADDRESS = "localhost"
                server = DocdDevServer(SPA_TEMPLATE,FILE_PATHS)
                server.listen(PORT,address=ADDRESS)
                print(f"Running at {ADDRESS}:{PORT}")
                await asyncio.Event().wait()

            asyncio.run(run_server())

        case _:
            print("ERROR: Failed to find command `{args.main_command}`")

