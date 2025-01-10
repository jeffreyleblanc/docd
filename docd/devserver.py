# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
Simple http file server.
"""

from pathlib import Path
import json
import asyncio
import tornado


class MainHandler(tornado.web.RequestHandler):
    def get(self, path):
        pkg = self.application.fetch_static_paths()
        html = self.application.SPA_TEMPLATE
        for k,v in pkg.items():
            html = html.replace(k,v)
        self.write(html)


class DocdDevServer(tornado.web.Application):

    def __init__(self, SPA_TEMPLATE, FILE_PATHS):
        self._handlers = []
        self._settings = {}
        self.initialize(SPA_TEMPLATE, FILE_PATHS)
        super().__init__(self._handlers,**self._settings)

    def initialize(self, SPA_TEMPLATE, FILE_PATHS):
        self.SPA_TEMPLATE  = SPA_TEMPLATE
        self.FILE_PATHS = FILE_PATHS

        # Handlers
        self._handlers += [
            # File Handlers
            (r"^/_resources/static/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["static"]}),
            (r"^/_resources/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["_resources"]}),
            # (r"^/_media/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["media"]}),
            # (r"^/_search/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["search"]}),
            # (r"^/static/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["static"]}),
            # Catch the rest of it as an SPA
            (r"^/(.*)", MainHandler),
        ]

        # Settings
        self._settings = dict(
            debug= True,
            autoreload= True
        )

    def fetch_static_paths(self):
        # Find the paths
        js_file = [ e for e in self.FILE_PATHS["static"].glob("*.js") ][0]
        css_file = [ e for e in self.FILE_PATHS["static"].glob("*.css") ][0]

        # Return the paths
        return {
            "__JS_FILE__":  f"/_resources/static/{js_file.name}",
            "__CSS_FILE__": f"/_resources/static/{css_file.name}",
        }
