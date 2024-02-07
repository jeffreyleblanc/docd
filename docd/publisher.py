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

@dataclass
class DocNode:
    kind: str                       # "directory" or "file"
    uri: Path                       # this is the visible uri for the page. this functions as the primary key
    parent_uri: Path                # this is uri of the "parent" or null if none
    depth: int
    db_uri: Path                    # this is the uri for the page source file in the database
    source_path: Path               # this is the relative filepath in the docs raw source
    display_name: str               # this is the name of the directory or file as displayed in the SPA
    display_suffix: str = None      # this is the suffix, if applicable, to be displayed in the SPA

    def to_dict(self):
        return {
            "kind": self.kind,
            "uri": str(self.uri),
            "parent_uri": None if self.parent_uri is None else str(self.parent_uri),
            "depth": self.depth,
            "db_uri": str(self.db_uri),
            "source_path": str(self.source_path),
            "display_name": self.display_name,
            "display_suffix": self.display_suffix
        }

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

        # Holder for
        self.doc_nodes = []

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
        self.doc_nodes = []
        root_node = self._unpack_dirs(self.SOURCE_ROOT,max_depth=2)

        # Write out the page database to a json file
        with Path(self.DEST_ROOT_DB/"page-db.json").open("w") as f:
            db = json.dumps([ e.to_dict() for e in self.doc_nodes ],indent=4)
            f.write(db)

        # Render the pages
        for info in self.doc_nodes:
            if info.kind == "directory":
                continue

            # Determine paths
            source = self.SOURCE_ROOT/info.source_path
            dest = self.DEST_ROOT_DB/info.db_uri

            # Ensure the folder exists
            dest.parent.mkdir(parents=True,exist_ok=True)

            # Add the contents
            language = FILE_MAP.get(source.suffix,"")
            content = self._render_page(source,language)

            # Write the file
            with dest.open("w") as f:
                f.write(content)


    def _unpack_dirs(self, directory_path, depth=0, max_depth=100000):

        # Calculate directory relpath
        directory_relpath = directory_path.relative_to(self.SOURCE_ROOT)
        # If we are the root, set the parent as None
        directory_parent_uri = str(directory_relpath.parent)
        if str(directory_relpath) == ".":
            directory_parent_uri = None
        # Display name exchanges '--' for ': '
        directory_display_name = directory_relpath.name.replace("--",": ")

        # Add the node for this directory
        self.doc_nodes.append(DocNode(
            kind = "directory",
            uri = directory_relpath,
            parent_uri = directory_parent_uri,
            depth = depth,
            db_uri = directory_relpath,
            source_path = directory_relpath,
            display_name = directory_display_name,
            display_suffix = None
        ))

        # Traverse the sources
        children = sorted([s for s in directory_path.iterdir()])
        for child_path in children:
            # Ignore skipped directories (Note should make deep path support)
            if child_path.is_dir() and child_path.name in SKIP_DIRECTORIES:
                continue

            # Get the relative child_path
            child_relpath = child_path.relative_to(self.SOURCE_ROOT)

            # If this is a file, add entry
            if child_path.is_file():

                # Pull out path components
                relpath_parent = child_relpath.parent
                _name = child_relpath.name
                _stem = child_relpath.stem
                _suffix = child_relpath.suffix

                # If it's a markdown file, set suffix to nothing
                # If it's not, set the stem to show the suffix
                if _suffix == ".md" or _suffix == "":
                    _suffix = ""
                else:
                    _stem += f"--dot-{_suffix[1:]}"

                # The database uri is always an html file
                child_db_uri = relpath_parent/f"{_stem}.html"

                # Display name exchanges '--' for ': '
                child_display_name = child_relpath.stem.replace("--",": ")

                # Add the node for this file
                self.doc_nodes.append(DocNode(
                    kind = "file",
                    uri = relpath_parent/_stem,
                    parent_uri = child_relpath.parent,
                    depth = depth,
                    db_uri = child_db_uri,
                    source_path = child_relpath,
                    display_name = child_display_name,
                    display_suffix = _suffix
                ))

            # If this is a directory, recurse or return depending on depth
            elif child_path.is_dir() and depth+1 <= max_depth:
                subnode = self._unpack_dirs(child_path,depth=depth+1,max_depth=max_depth)


    def _render_page(self, source_path, language):
        if language == "markdown":
            return make_html(source_path.read_text())
        else:
            code = source_path.read_text()
            txt = f"```{language}\n{code}\n```"
            return make_html(txt)


