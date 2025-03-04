# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

# Python
from pathlib import Path
import json
import uuid
from dataclasses import dataclass
import datetime
import shutil
# Lunr
from lunr import lunr
# Local
from docd.utils.markdown2html import make_html
from docd.utils.proc import local_rsync


SKIP_DIRECTORIES = (".git","_output","_media")

@dataclass
class DocNode:
    kind: str                       # "directory" or "file"
    uri: Path                       # this is the visible uri for the page. this functions as the primary key
    parent_uri: Path                # this is uri of the "parent" or null if none
    depth: int
    source_path: Path               # this is the relative filepath in the docs raw source
    display_name: str               # this is the name of the directory or file as displayed in the SPA
    display_suffix: str = None      # this is the suffix, if applicable, to be displayed in the SPA
    last_modified: datetime.datetime = None

    def to_dict(self):
        return {
            "kind": self.kind,
            "uri": str(self.uri),
            "parent_uri": None if self.parent_uri is None else str(self.parent_uri),
            "depth": self.depth,
            "source_path": str(self.source_path),
            "display_name": self.display_name,
            "display_suffix": self.display_suffix,
            "last_modified": self.last_modified.isoformat()
        }

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
        self.DEST_PAGES_TXT_DIR =  self.DEST_RESOURCES_DIR/"pages-txt"
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
        self.DEST_PAGES_TXT_DIR.mkdir(exist_ok=True)
        self.DEST_MEDIA_DIR.mkdir(exist_ok=True)
        self.DEST_SEARCH_DIR.mkdir(exist_ok=True)
        self.DEST_STATIC_DIR.mkdir(exist_ok=True)

    #-- Build Pages --------------------------------------------------------#

    def build_docs(self):
        # Build our doc nodes
        self._build_set_of_doc_nodes()

        # Synchronize the media folder
        media_src = self.SOURCE_ROOT/"_media"
        if media_src.is_dir():
            c,o,e = local_rsync(media_src,self.DEST_MEDIA_DIR,delete=True)
            if c != 0:
                print(c,o,e)
                raise Exception("Rsync of _media failed")

        # Write out the page database to a json file
        with self.DEST_PAGES_DB_FILE.open("w") as f:
            db = json.dumps([ e.to_dict() for e in self.doc_nodes ],indent=4)
            f.write(db)

        # Render the pages
        # ==> could be made smarter to only create new/modified sources
        for info in self.doc_nodes:
            if info.kind == "directory":
                continue

            # Determine paths
            source = self.SOURCE_ROOT/info.source_path
            dest = self.DEST_PAGES_HTML_DIR/f"{info.uri}.html"

            # Ensure the folder exists
            dest.parent.mkdir(parents=True,exist_ok=True)

            # Add the contents
            language = self.FILE_MAP.get(source.suffix,"")
            content = self._create_html_page(source,language)

            # Write the file
            with dest.open("w") as f:
                f.write(content)

        # Copy over the raw pages
        # ==> could be made smarter to only copy changes
        for info in self.doc_nodes:
            if info.kind == "directory":
                continue

            # Determine paths
            source = self.SOURCE_ROOT/info.source_path
            dest = self.DEST_PAGES_TXT_DIR/f"{info.uri}.txt"

            # Ensure the folder exists
            dest.parent.mkdir(parents=True,exist_ok=True)

            # Copy the file
            shutil.copy(source,dest)


    def _create_html_page(self, source_path, language):
        if language == "markdown":
            return make_html(source_path.read_text())
        else:
            code = source_path.read_text()
            txt = f"```{language}\n{code}\n```"
            return make_html(txt)


    #-- Search System ---------------------------------------------------------------------------#

    def build_search_index(self):
        self._build_set_of_doc_nodes()
        DOCS = self._create_document_set_for_lunr()

        # Generate the indexer
        indexer = lunr(ref="path",fields=("title","body"),documents=DOCS)

        # Output the serialized index
        serialized_index = indexer.serialize()
        with self.DEST_SEARCH_INDEX_FILE.open("w") as fp:
            json.dump(serialized_index,fp,indent=None)


    def _create_document_set_for_lunr(self):
        DOCS = []
        for docnode in self.doc_nodes:
            if docnode.kind != "file":
                continue
            ref = str(docnode.uri)
            entry = {
                "path": ref,
                "title": ref,
                "body": ""
            }
            with (self.SOURCE_ROOT/docnode.source_path).open("r") as fp:
                entry["body"] = fp.read()
            DOCS.append(entry)

        return DOCS


    #-- Source walker and Page Makers ------------------------------------------------------#

    def _build_set_of_doc_nodes(self):
        # Parse the docs directory
        self.doc_nodes = []
        self._walk_and_unpack_source_directory(self.SOURCE_ROOT,max_depth=self.max_directory_depth)

    def _walk_and_unpack_source_directory(self, directory_path, depth=0, max_depth=100000):
        # Calculate directory relpath
        directory_relpath = directory_path.relative_to(self.SOURCE_ROOT)

        # If we are the root, set the parent as None
        directory_parent_uri = str(directory_relpath.parent)
        if str(directory_relpath) == ".":
            directory_parent_uri = None

        # Display name exchanges '--' for ': '
        directory_display_name = directory_relpath.name.replace("--",": ")

        # Get the modified time
        modified_time = datetime.datetime.fromtimestamp(directory_path.stat().st_mtime)

        # Add the node for this directory
        self.doc_nodes.append(DocNode(
            kind = "directory",
            uri = directory_relpath,
            parent_uri = directory_parent_uri,
            depth = depth,
            source_path = directory_relpath,
            display_name = directory_display_name,
            display_suffix = None,
            last_modified = modified_time
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

                # Display name exchanges '--' for ': '
                child_display_name = child_relpath.stem.replace("--",": ")

                # Get the modified time
                modified_time = datetime.datetime.fromtimestamp(child_path.stat().st_mtime)

                # Add the node for this file
                self.doc_nodes.append(DocNode(
                    kind = "file",
                    uri = relpath_parent/_stem,
                    parent_uri = child_relpath.parent,
                    depth = depth,
                    source_path = child_relpath,
                    display_name = child_display_name,
                    display_suffix = _suffix,
                    last_modified = modified_time
                ))

            # If this is a directory, recurse or return depending on depth
            elif child_path.is_dir() and depth+1 <= max_depth:
                subnode = self._walk_and_unpack_source_directory(child_path,depth=depth+1,max_depth=max_depth)
