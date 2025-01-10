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
        # self.write(f"hello from docd: {path}")
        # self.render("index.html")
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

    def fetch_static_paths(self):
        print("STATIC????")
        js_raw = [ e for e in self.FILE_PATHS["static"].glob("*.js") ][0]
        css_raw = [ e for e in self.FILE_PATHS["static"].glob("*.css") ][0]

        pkg = {
            "__JS_FILE__": "/static/"+str(js_raw.relative_to(self.FILE_PATHS["static"])),
            "__CSS_FILE__": "/static/"+str(css_raw.relative_to(self.FILE_PATHS["static"])),
        }
        print("pkg:",pkg)
        return pkg

    def initialize(self, SPA_TEMPLATE, FILE_PATHS):
        self.SPA_TEMPLATE  = SPA_TEMPLATE
        self.FILE_PATHS = FILE_PATHS

        # Handlers
        self._handlers += [
            # File Handlers
            (r"^/db/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["db"]}),
            (r"^/_media/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["media"]}),
            (r"^/_search/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["search"]}),
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {"path": self.FILE_PATHS["static"]}),
            # Catch the rest of it as an SPA
            (r"^/(.*)", MainHandler),
        ]

        # Settings
        self._settings = dict(
            debug= True,
            autoreload= True
        )
