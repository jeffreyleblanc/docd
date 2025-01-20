# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
Simple http file server.
"""

from pathlib import Path
import json
import asyncio
import tornado
# Local
from docd.spa import render_spa_html
from docd.utils.filetools import find_one_matching_file


class MainHandler(tornado.web.RequestHandler):
    def get(self, path):
        pkg = self.application.fetch_static_paths()
        html = render_spa_html(pkg,template_text=self.application.SPA_TEMPLATE)
        self.write(html)


class DocdDevServer(tornado.web.Application):

    def __init__(self, SPA_TEMPLATE=None, FILE_PATHS=None, ROOT_URI=None):
        self.SPA_TEMPLATE  = SPA_TEMPLATE
        self.FILE_PATHS = FILE_PATHS
        self.ROOT_URI = ROOT_URI

        self._handlers = []
        self._settings = {}

        self.initialize()
        super().__init__(self._handlers,**self._settings)

    def initialize(self):
        # Handlers
        self._handlers += [
            # File Handlers
            (rf"^{self.ROOT_URI}/_resources/static/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["static"]}),
            (rf"^{self.ROOT_URI}/_resources/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["_resources"]}),
            # Catch the rest of it as an SPA
            (fr"^{self.ROOT_URI}/(.*)", MainHandler),
        ]

        # Settings
        self._settings = dict(
            debug= True,
            autoreload= True
        )

    def fetch_static_paths(self):
        # Find the paths
        JS_FILE = find_one_matching_file(self.FILE_PATHS["static"],"*.js")
        CSS_FILE = find_one_matching_file(self.FILE_PATHS["static"],"*.css")

        # Return the paths
        return {
            "__JS_FILE__":  f"{self.ROOT_URI}/_resources/static/{JS_FILE.name}",
            "__CSS_FILE__": f"{self.ROOT_URI}/_resources/static/{CSS_FILE.name}",
        }
