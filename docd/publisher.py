# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

# Python
from pathlib import Path
import json
import uuid
from dataclasses import dataclass
# Libraries
from mako.template import Template
from mako.lookup import TemplateLookup
# Local
from docd.utils.markdown2html import make_html
from docd.utils.proc import rsync
from docd.utils.filetools import clear_directory

@dataclass
class Category:
    kind =  "category"
    name:   str = None
    uri:    str = None
    # parent_path

@dataclass
class FileRep:
    kind =  "file"
    name:   str = None
    source: Path = None
    dest:   Path = None
    uri:    str = None
    # parent_path

"""
kind:           "directory" or "file"
uri:            this is the visible uri for the page
                this functions as the primary key
parent_uri:     this is uri of the "parent" or null if none
db_uri:         this is the uri for the page source file in the database
source_path:    this is the relative filepath in the docs raw source
display_name:   this is the name of the directory or file as displayed in the SPA
display_suffix: this is the suffix, if applicable, to be displayed in the SPA
"""


FILE_MAP = {
    ".md":"markdown",
    ".py":"python",
    ".txt":"",
    ".html":"html",
    ".sh":"bash",
    ".bash":"bash",
    ".vue":"html",
    ".js":"javascript",
    ".css":"css",
    ".conf":"bash"
}

SKIP_DIRECTORIES = (".git","_output","_media")

class Publisher:

    def __init__(self, ctx, site_config):
        # Save the config
        self.site_config = site_config

        # Establish base paths
        self.REPO_ROOT = ctx.DOCS_REPO_DIRPATH
        self.SOURCE_ROOT = ctx.DOCS_DOCS_DIRPATH
        self.DEST_ROOT = ctx.DOCS_DIST_DIRPATH
        self.DEST_ROOT_DB = ctx.DOCS_DIST_DIRPATH/"db"

        # Load the html template
        self.SUPPORT_RESOURCES_DIRPATH = ctx.SUPPORT_RESOURCES_DIRPATH
        _template_dir = self.SUPPORT_RESOURCES_DIRPATH/"templates/"
        _template_lookup = TemplateLookup(directories=[_template_dir])
        self.SPA_TEMPLATE = _template_lookup.get_template("spa.html")

        # Initialize all paths
        self.all_paths_list = []

    #-- Build --------------------------------------------------------#

    def _build_setup(self):
        # Make our output root
        self.DEST_ROOT.mkdir(exist_ok=True)

    def build_spa(self):
        self._build_setup()

        # Synchronize static directory
        SRC_STATIC = self.SUPPORT_RESOURCES_DIRPATH/"static"
        DEST_STATIC = self.DEST_ROOT/"static"
        DEST_STATIC.mkdir(exist_ok=True)
        c,o,e = rsync(SRC_STATIC,DEST_STATIC,delete=True,exclude=[".gitkeep"])
        if c != 0:
            print(c,o,e)
            raise Exception("Rsync of static failed")

        # Make the spa page with embedded page database
        html = self.SPA_TEMPLATE.render(
            title=self.site_config.title,
            name=self.site_config.name,
            footer=self.site_config.footer,
            home_addr=self.site_config.home_addr,
            rh=uuid.uuid4().hex[:6]
        )
        with Path(self.DEST_ROOT/"index.html").open("w") as f:
            f.write(html)

    def build_docs(self):
        self._build_setup()
        self.DEST_ROOT_DB.mkdir(exist_ok=True)

        # Synchronize the media folder
        media_src = self.SOURCE_ROOT/"_media"
        if media_src.is_dir():
            media_dest = self.DEST_ROOT/"_media"
            media_dest.mkdir(exist_ok=True)
            c,o,e = rsync(media_src,media_dest,delete=True)
            if c != 0:
                print(c,o,e)
                raise Exception("Rsync of _media failed")

        # Parse the docs directory
        self.flat_file_map = {}
        self.LIST = []
        root_node = self._unpack_dirs(self.SOURCE_ROOT,max_depth=2)

        # Write out the page database to a json file
        with Path(self.DEST_ROOT_DB/"page-db.json").open("w") as f:
            db = json.dumps(self.LIST,indent=4)
            f.write(db)

        # Render the pages
        for info in self.LIST:
            if info["kind"] == "directory":
                continue

            # Determine paths
            source = self.SOURCE_ROOT/info["source_path"]
            dest = self.DEST_ROOT_DB/info["db_uri"]

            # Ensure the folder exists
            dest.parent.mkdir(parents=True,exist_ok=True)

            # Add the contents
            language = FILE_MAP.get(source.suffix,"")
            content = self._render_page(source,language)

            # Write the file
            with dest.open("w") as f:
                f.write(content)


    def _unpack_dirs(self, SOURCE_ROOT, depth=0, max_depth=100000):
        indent = " "*(4*depth)
        # print(f"{indent}UNPACK",SOURCE_ROOT.name,depth)

        curr_path = SOURCE_ROOT.relative_to(self.SOURCE_ROOT)
        _p_uri = str(curr_path.parent)
        if str(curr_path) == ".":
            _p_uri = None
        NODE = {
            "kind": "directory",
            "uri": str(curr_path),
            "parent_uri": _p_uri,
            "depth": depth,
            "db_uri": str(curr_path),
            "source_path": str(curr_path),
            "display_name": curr_path.name.replace("--",":"),
            "display_suffix": None
        }
        self.LIST.append(NODE)

        # Traverse the sources
        srcs = sorted([s for s in SOURCE_ROOT.iterdir()])
        for path in srcs:
            # Ignore skipped directories (Note should make deep path support)
            if path.is_dir() and path.name in SKIP_DIRECTORIES:
                continue

            # Get the relative path
            relpath = path.relative_to(self.SOURCE_ROOT)

            # If this is a file, add entry
            if path.is_file():

                relpath_parent = relpath.parent
                _name = relpath.name
                _stem = relpath.stem
                _suffix = relpath.suffix

                if _suffix == ".md" or _suffix == "":
                    _suffix = ""
                else:
                    _stem += f"--dot-{_suffix[1:]}"

                FNODE = {
                    "kind": "file",
                    "uri": str(relpath_parent/_stem),
                    "parent_uri": str(relpath.parent),
                    "depth": depth,
                    "db_uri": str(relpath_parent/_stem)+".html",
                    "source_path": str(relpath),
                    "display_name": relpath.stem.replace("--",":"),
                    "display_suffix": _suffix
                }
                self.LIST.append(FNODE)

            # If this is a directory, parse or return
            elif path.is_dir() and depth+1 <= max_depth:
                subnode = self._unpack_dirs(path,depth=depth+1,max_depth=max_depth)


    def _render_page(self, source_path, language):
        if language == "markdown":
            return make_html(source_path.read_text())
        else:
            code = source_path.read_text()
            txt = f"```{language}\n{code}\n```"
            return make_html(txt)


