# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

# Python
from pathlib import Path
import json
import uuid
from dataclasses import dataclass
# Lunr
from lunr import lunr
# Local
from docd.utils.markdown2html import make_html
from docd.utils.proc import rsync


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

"""
_dist/
    index.html # spa
    _resources
        pages-database.json
        pages-html/
            ... all the pages
        media/
            ... media support
        search/
            ... search tooling
        static/
            ... static tooling

"""

class Publisher:

    def __init__(self, ctx, config):
        # Save the config
        self.site_config = config.site
        self.max_directory_depth = config.source.max_depth
        self.FILE_MAP = config.source.file_types

        # Establish base paths
        self.REPO_ROOT = ctx.DOCS_REPO_DIRPATH
        self.SOURCE_ROOT = ctx.DOCS_DOCS_DIRPATH

        # Destination paths
        self.DEST_ROOT = ctx.DOCS_DIST_DIRPATH
        self.DEST_RESOURCES_DIR = ctx.DOCS_DIST_DIRPATH/"_resources"
        self.DEST_PAGES_DB_FILE = self.DEST_RESOURCES_DIR/"pages-database.json"
        self.DEST_PAGES_HTML_DIR = self.DEST_RESOURCES_DIR/"pages-html"
        self.DEST_MEDIA_DIR = self.DEST_RESOURCES_DIR/"media"
        self.DEST_SEARCH_DIR = self.DEST_RESOURCES_DIR/"search"
        self.DEST_SEARCH_INDEX_FILE = self.DEST_SEARCH_DIR/"serialized-index.json"
        self.DEST_STATIC_DIR = self.DEST_RESOURCES_DIR/"static"

        # Depth and Holder for nodes
        self.doc_nodes = []

    #-- Build Structure--------------------------------------------------------#

    def build_dest_directory_structure(self):
        # Make our output root
        self.DEST_ROOT.mkdir(exist_ok=True)

        # Make all of our subdirectories
        self.DEST_RESOURCES_DIR.mkdir(exist_ok=True)
        self.DEST_PAGES_HTML_DIR.mkdir(exist_ok=True)
        self.DEST_MEDIA_DIR.mkdir(exist_ok=True)
        self.DEST_SEARCH_DIR.mkdir(exist_ok=True)
        self.DEST_STATIC_DIR.mkdir(exist_ok=True)

    #-- Build Pages --------------------------------------------------------#

    def build_docs(self):
        # Synchronize the media folder
        media_src = self.SOURCE_ROOT/"_media"
        if media_src.is_dir():
            c,o,e = rsync(media_src,self.DEST_MEDIA_DIR,delete=True)
            if c != 0:
                print(c,o,e)
                raise Exception("Rsync of _media failed")

        # Parse the docs directory
        self.doc_nodes = []
        root_node = self._unpack_source_directory(self.SOURCE_ROOT,max_depth=self.max_directory_depth)

        # Write out the page database to a json file
        with self.DEST_PAGES_DB_FILE.open("w") as f:
            db = json.dumps([ e.to_dict() for e in self.doc_nodes ],indent=4)
            f.write(db)

        # Render the pages
        for info in self.doc_nodes:
            if info.kind == "directory":
                continue

            # Determine paths
            source = self.SOURCE_ROOT/info.source_path
            dest = self.DEST_PAGES_HTML_DIR/info.db_uri

            # Ensure the folder exists
            dest.parent.mkdir(parents=True,exist_ok=True)

            # Add the contents
            language = self.FILE_MAP.get(source.suffix,"")
            content = self._create_html_page(source,language)

            # Write the file
            with dest.open("w") as f:
                f.write(content)


    #-- Source walker and Page Makers ------------------------------------------------------#

    def _unpack_source_directory(self, directory_path, depth=0, max_depth=100000):
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

            # If this is a file, add entry
            if child_path.is_file():

                # Get the relative child_path
                child_relpath = child_path.relative_to(self.SOURCE_ROOT)

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
                subnode = self._unpack_source_directory(child_path,depth=depth+1,max_depth=max_depth)


    def _create_html_page(self, source_path, language):
        if language == "markdown":
            return make_html(source_path.read_text())
        else:
            code = source_path.read_text()
            txt = f"```{language}\n{code}\n```"
            return make_html(txt)

    #-- Search System ---------------------------------------------------------------------------#

    def build_search_index(self):
        DOCS = self._create_document_set_for_lunr()

        # Generate the indexer
        indexer = lunr(ref="path",fields=("title","body"),documents=DOCS)

        # Output the serialized index
        serialized_index = indexer.serialize()
        with self.DEST_SEARCH_INDEX_FILE.open("w") as fp:
            json.dump(serialized_index,fp,indent=None)


    def _create_document_set_for_lunr(self):
        DOCS = []
        for fpath in sorted(self.SOURCE_ROOT.glob("**/*.md")):
            ref = fpath.relative_to(self.SOURCE_ROOT)
            entry = {
                "path": ref,
                "title": ref,
                "body": ""
            }
            with fpath.open("r") as fp:
                entry["body"] = fp.read()
            DOCS.append(entry)

        return DOCS