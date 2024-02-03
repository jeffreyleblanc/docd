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


FILE_MAP = {
    ".md":"markdown",
    ".py":"python",
    ".txt":"",
    ".html":"html",
    ".sh":"bash",
    ".bash":"bash",
    ".vue":"html",
    ".js":"javascript",
    ".css":"css"
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

        # NEW: Support Media
        media_src = self.SOURCE_ROOT/"_media"
        if media_src.is_dir():
            media_dest = self.DEST_ROOT/"_media"
            media_dest.mkdir(exist_ok=True)
            c,o,e = rsync(media_src,media_dest,delete=True)
            if c != 0:
                print(c,o,e)
                raise Exception("Rsync of _media failed")

        print("Begin new file parser")

        self.flat_file_map = {}

        def _unpack_dirs(SOURCE_ROOT, depth=0, max_depth=100000):
            indent = " "*(4*depth)
            print(f"{indent}UNPACK",SOURCE_ROOT.name,depth)

            node = {
                "depth": depth,
                "kind": "directory",
                "path": str(SOURCE_ROOT.relative_to(self.SOURCE_ROOT)),
                "name": SOURCE_ROOT.name,
                "files": [],
                "directories": []
            }

            # Traverse the sources
            srcs = sorted([s for s in SOURCE_ROOT.iterdir()])
            for path in srcs:
                # Ignore skipped directories (Note should make deep path support)
                if path.is_dir() and path.name in SKIP_DIRECTORIES:
                    continue

                relpath = path.relative_to(self.SOURCE_ROOT)

                if path.is_file():
                    uriupp = relpath.parent
                    uri = str(uriupp/path.stem)
                    if path.suffix != ".md":
                        uri += f"--dot-{path.suffix[1:]}"

                    fnode = {
                        "depth": depth,
                        "kind": "file",
                        "path": str(relpath),
                        "name": path.name,
                        "stem": path.stem,
                        "suffix": path.suffix,
                        "db_file_path": None,
                        "uri": uri
                    }
                    node["files"].append(fnode)
                    self.flat_file_map[str(relpath)] = fnode
                elif path.is_dir() and depth+1 <= max_depth:
                    subnode = _unpack_dirs(path,depth=depth+1,max_depth=max_depth)
                    node["directories"].append(subnode)

            return node


        root_node = _unpack_dirs(self.SOURCE_ROOT,max_depth=2)
        print("-"*32)
        print(json.dumps(root_node,indent=4))
        print(json.dumps(self.flat_file_map,indent=4))

        return

        ## Reset Paths #########################################

        self.all_paths_list = []

        ## Process the Directories #########################################

        # Break this into chunks

        # Make the main page
        main_page = self.SOURCE_ROOT/"__main__.md"
        if main_page.is_file():
            main_source = main_page.read_text()
        else:
            main_source = "Some documentation."
        main_html = make_html(main_source)
        with Path(self.DEST_ROOT_DB/"__main__.html").open("w") as f:
            f.write(main_html)

        # Traverse the sources
        srcs = sorted([s for s in self.SOURCE_ROOT.iterdir()])
        for srcdir in srcs:
            # Ignore files in root directory
            if not srcdir.is_dir():
                continue
            # Ignore more files
            if srcdir.name in SKIP_DIRECTORIES:
                continue

            # Render found files
            self._process_directory(srcdir,srcdir.name,FILE_MAP)

        ## Make database #########################################

        # Make the index database
        page_database = []
        curr_pages = None
        for item in self.all_paths_list:
            if item.kind == "category":
                curr_pages = []
                page_database.append({
                    "kind":"category",
                    "name":item.name,
                    "pages":curr_pages
                })
            else:
                curr_pages.append({
                    "name":item.name,
                    "uri":item.uri
                })

        # Write out the page database to a json file
        with Path(self.DEST_ROOT_DB/"page-db.json").open("w") as f:
            db = json.dumps(page_database,indent=4)
            f.write(db)

    #-- Helpers ----------------------------------------------------------------#

    def _process_directory(self, source_directory, out_uri, suffix_lang_map):
        # Make the target directory
        TGT = self.DEST_ROOT_DB/out_uri
        TGT.mkdir(exist_ok=True)

        self.all_paths_list.append(Category(name=out_uri))

        # Gather all filenames
        sources = []
        for s in source_directory.iterdir():
            if s.suffix not in suffix_lang_map: continue
            sources.append(FileRep(
                name= s.stem,
                source= s,
                dest= TGT/f"{s.stem}.html",
                uri= f"/{out_uri}/{s.stem}.html"
            ))
        sources.sort(key=lambda e: e.name)
        self.all_paths_list += sources

        # Generate the files
        for item in sources:
            # Add the contents
            language = suffix_lang_map.get(item.source.suffix)
            content = self._render_page(item.source,language)

            # Write the file
            with item.dest.open("w") as f:
                f.write(content)

    def _render_page(self, source_path, language):
        if language == "markdown":
            return make_html(source_path.read_text())
        else:
            code = source_path.read_text()
            txt = f"```{language}\n{code}\n```"
            return make_html(txt)


