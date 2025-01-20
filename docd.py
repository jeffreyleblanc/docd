#! /usr/bin/env python3

# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import argparse
from pathlib import Path
from dataclasses import dataclass
import shutil
import toml
import json
from docd.utils.proc import proc, rsync
from docd.utils.obj import DictObj
from docd.utils.filetools import clear_directory, find_one_matching_file
from docd.spa import render_spa_html


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
    # Set an empty home_addr if none
    if "home_addr" not in config.site:
        config.site.home_addr = ""
    # Check on the site.root_uri
    if "root_uri" not in config.site:
        config.site.root_uri = ""
    else:
        assert config.site.root_uri.startswith("/")
        assert not config.site.root_uri.endswith("/")

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
    A = subparsers.add_parser

    # Main commands
    A("clean-dist", help="Clean out the docd site")
    A("build-pages", help="Build the rendered pages")
    A("build-search", help="Build the search index")
    A("build-spa", help="Build the dist spa")
    A("devserver", help="Run the new server")
    a = A("developer", help="Docd developer tools")
    a.add_argument("devcmd",choices=("clear-spa-framework","build-spa-framework"))

    # Older
    A("push", help="Push docs to a remote")
    A("check", help="Check docs for filter phrases")
    A("info", help="Print info on the repo config")

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
    else:
        ctx.IN_DOCD_SOURCE_REPO = True

    #-- Execute the Commands -----------------------------------------------------------#

    if "developer" == args.main_command:
        # Determine paths
        SPA_SRC_DIR = Path("spa-src")
        SPA_SRC_STATIC_DIR = SPA_SRC_DIR/"dist/static"
        SPA_DIST_DIR = Path("spa-framework-dist/dist")

        if "clear-spa-framework" == args.devcmd:
            if SPA_DIST_DIR.is_dir():
                clear_directory(SPA_DIST_DIR)

        elif "build-spa-framework" == args.devcmd:
            # Build the js/css with vite
            print("Building the js/css with vite:")
            c,o,e = proc("npx vite build",cwd=SPA_SRC_DIR)
            print(c,o,e)

            # Set the spa-dist directory
            SPA_DIST_DIR = Path("spa-framework-dist/dist")

            # Build and clear the spa-dist static directory
            SPA_DIST_STATIC_DIR = SPA_DIST_DIR/"static"
            SPA_DIST_STATIC_DIR.mkdir(exist_ok=True,parents=True)
            clear_directory(SPA_DIST_STATIC_DIR)

            # Determine the js/css paths
            JS_FILE = find_one_matching_file(SPA_SRC_STATIC_DIR,"*.js")
            CSS_FILE = find_one_matching_file(SPA_SRC_STATIC_DIR,"*.css")

            # Copy the paths to spa-dist
            shutil.copy(JS_FILE,SPA_DIST_STATIC_DIR/JS_FILE.name)
            shutil.copy(CSS_FILE,SPA_DIST_STATIC_DIR/CSS_FILE.name)

            # Write out the static resource names
            with (SPA_DIST_DIR/"static-resources.json").open("w") as fp:
                fp.write(json.dumps({
                    "js_file_name": JS_FILE.name,
                    "css_file_name": CSS_FILE.name
                },indent=4))


    else:
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

        # Execute the command
        match args.main_command:

            case "clean-dist":
                import shutil
                assert ctx.DOCS_DIST_DIRPATH.is_dir()
                clear_directory(ctx.DOCS_DIST_DIRPATH)

            case "build-pages":
                from docd.publisher import Publisher
                pub = Publisher(ctx,config)
                pub.build_dest_directory_structure()
                pub.build_docs()

            case "build-search":
                from docd.publisher import Publisher
                pub = Publisher(ctx,config)
                pub.build_dest_directory_structure()
                pub.build_search_index()

            case "build-spa":
                # Define paths
                SPA_DIST_DIR = Path("spa-framework-dist/dist")
                SPA_DIST_STATIC_DIR = SPA_DIST_DIR/"static"

                # Load the static info
                static_info = json.loads((SPA_DIST_DIR/"static-resources.json").read_text())

                # Make the spa html
                spa_html = render_spa_html({
                    "__TITLE__":    config.site.title,
                    "__AUTHOR__":   config.site.author,
                    "__NAME__" :    config.site.name,
                    "__FOOTER__":   config.site.footer,
                    "__HOME_URL__": config.site.home_addr,
                    "__CSS_FILE__": f"{config.site.root_uri}/_resources/static/{static_info['css_file_name']}",
                    "__JS_FILE__":  f"{config.site.root_uri}/_resources/static/{static_info['js_file_name']}"
                })

                # Write it to file
                DIST_SPA_FILE = ctx.DOCS_DIST_DIRPATH/"index.html"
                with DIST_SPA_FILE.open("w") as f:
                    f.write(spa_html)

                # Sync over the static assets
                STATIC_DIR = ctx.DOCS_DIST_DIRPATH/"_resources/static"
                STATIC_DIR.mkdir(exist_ok=True)
                rsync(SPA_DIST_STATIC_DIR,STATIC_DIR,delete=True)

            case "devserver":
                import asyncio
                from docd.devserver import DocdDevServer

                # Make a temporary config for now
                # Leave off the css and js as those will be dynamically added
                rendered_spa_html = render_spa_html({
                    "__TITLE__":    config.site.title,
                    "__AUTHOR__":   config.site.author,
                    "__NAME__" :    config.site.name,
                    "__FOOTER__":   config.site.footer,
                    "__HOME_URL__": config.site.home_addr
                })

                # Set the static directory as where vite builds to
                STATIC_DIR = Path("spa-src/dist/static")

                # Set the file paths
                FILE_PATHS = dict(
                    _resources = ctx.DOCS_DIST_DIRPATH/"_resources",
                    static = STATIC_DIR
                )

                async def run_server():
                    PORT = 8100
                    ADDRESS = "localhost"
                    server = DocdDevServer(rendered_spa_html,FILE_PATHS)
                    server.listen(PORT,address=ADDRESS)
                    print(f"Running at {ADDRESS}:{PORT}")
                    await asyncio.Event().wait()

                asyncio.run(run_server())

        ## Older #################################################

        """
        case "info":
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            print("# args:")
            pp.pprint(args)
            print("\n# ctx:")
            pp.pprint(ctx)
            print("\n# config:")
            print(json.dumps(config.to_dict(),indent=4))

        case "check":
            import docd.cmd_check as CHECK
            CHECK.main_run(ctx,config)

        case "push":
            #==> use the rsync tool from utils.proc

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

        case _:
            print("ERROR: Failed to find command `{args.main_command}`")
        """
