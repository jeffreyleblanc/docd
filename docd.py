#! /usr/bin/env python3

# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

import argparse
from pathlib import Path
from dataclasses import dataclass
import shutil
import toml
import json
from docd.utils.proc import proc, local_rsync
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


def main():
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
    HERE = Path(__file__).parent
    if HERE == Path("/usr/local/bin"):
        ctx.IN_DOCD_SOURCE_REPO = False
    else:
        ctx.IN_DOCD_SOURCE_REPO = True

    #-- Common Paths -------------------------------------------------------------------#

    # spa-src/ paths
    SPA_SRC_DIR = Path("spa-src").resolve()
    SPA_SRC_STATIC_DIST_STATIC_DIR = SPA_SRC_DIR/"dist/static"
    # spa-framework-dist/ paths
    SPA_FRAMEWORK_DIST_DIR = Path("spa-framework-dist/dist").resolve()
    SPA_FRAMEWORK_DIST_STATIC_DIR = SPA_FRAMEWORK_DIST_DIR/"static"
    SPA_FRAMEWORK_DIST_RESOURCES_JSON_FILE = SPA_FRAMEWORK_DIST_DIR/"static-resources.json"

    #-- Execute the Commands -----------------------------------------------------------#

    if "developer" == args.main_command:
        if "clear-spa-framework" == args.devcmd:
            if SPA_FRAMEWORK_DIST_DIR.is_dir():
                clear_directory(SPA_FRAMEWORK_DIST_DIR)

        elif "build-spa-framework" == args.devcmd:
            # Build the js/css with vite
            print("Building the js/css with vite:")
            c,o,e = proc("npx vite build",cwd=SPA_SRC_DIR)
            print(c,o,e)

            # Build and clear the spa-dist static directory
            SPA_FRAMEWORK_DIST_STATIC_DIR.mkdir(exist_ok=True,parents=True)
            clear_directory(SPA_FRAMEWORK_DIST_STATIC_DIR)

            # Determine the js/css paths
            JS_FILE = find_one_matching_file(SPA_SRC_STATIC_DIST_STATIC_DIR,"*.js")
            CSS_FILE = find_one_matching_file(SPA_SRC_STATIC_DIST_STATIC_DIR,"*.css")

            # Copy the paths to spa-dist
            shutil.copy(JS_FILE,SPA_FRAMEWORK_DIST_STATIC_DIR/JS_FILE.name)
            shutil.copy(CSS_FILE,SPA_FRAMEWORK_DIST_STATIC_DIR/CSS_FILE.name)

            # Write out the static resource names
            with SPA_FRAMEWORK_DIST_RESOURCES_JSON_FILE.open("w") as fp:
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
                # Load the static info
                static_info = json.loads(SPA_FRAMEWORK_DIST_RESOURCES_JSON_FILE.read_text())

                # Make the spa html
                spa_html = render_spa_html({
                    "__ROOT_URI__": config.site.root_uri,
                    "__TITLE__":    config.site.title,
                    "__AUTHOR__":   config.site.author,
                    "__NAME__" :    config.site.name,
                    "__FOOTER__":   config.site.footer,
                    "__HOME_URL__": config.site.home_addr,
                    "__CSS_FILE__": f"{config.site.root_uri}/_resources/static/{static_info['css_file_name']}",
                    "__JS_FILE__":  f"{config.site.root_uri}/_resources/static/{static_info['js_file_name']}"
                })

                # Write it to file
                _DIST_SPA_FILE = ctx.DOCS_DIST_DIRPATH/"index.html"
                with _DIST_SPA_FILE.open("w") as f:
                    f.write(spa_html)

                # Sync over the static assets
                _STATIC_DIR = ctx.DOCS_DIST_DIRPATH/"_resources/static"
                _STATIC_DIR.mkdir(exist_ok=True,parents=True)
                local_rsync(SPA_FRAMEWORK_DIST_STATIC_DIR,_STATIC_DIR,delete=True)

            case "devserver":
                import asyncio
                from docd.devserver import DocdDevServer

                # Make a rendered spa template
                # Leave off the css and js as those will be dynamically added
                rendered_spa_html = render_spa_html({
                    "__ROOT_URI__": config.site.root_uri,
                    "__TITLE__":    config.site.title,
                    "__AUTHOR__":   config.site.author,
                    "__NAME__" :    config.site.name,
                    "__FOOTER__":   config.site.footer,
                    "__HOME_URL__": config.site.home_addr
                })

                # Set the file paths
                FILE_PATHS = dict(
                    _resources = ctx.DOCS_DIST_DIRPATH/"_resources",
                    static = SPA_SRC_STATIC_DIST_STATIC_DIR
                )

                async def run_server():
                    PORT = 8100
                    ADDRESS = "localhost"
                    server = DocdDevServer(
                        rendered_spa_html,
                        FILE_PATHS,
                        config.site.root_uri
                    )
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
            #==> use the local_rsync tool from utils.proc

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

            # Make the local_rsync command
            cmd = f"local_rsync -avz --delete {src} {user}@{addr}:{dst}"
            c,o,e = proc(cmd)
            print(c,o,e)

        case _:
            print("ERROR: Failed to find command `{args.main_command}`")
        """

if __name__ == "__main__":
    main()
