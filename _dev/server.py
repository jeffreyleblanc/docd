# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
Simple http file server.
"""
#! /usr/bin/env python3

from pathlib import Path
import json
import asyncio
import tornado


class MainHandler(tornado.web.RequestHandler):
    def get(self, path):
        self.write(f"hello from docd: {path}")
        # self.render("index.html")


class MyApp(tornado.web.Application):

    def __init__(self):
        self._handlers = []
        self._settings = {}
        self.initialize()
        super().__init__(self._handlers,**self._settings)

    def initialize(self):
        # Get our paths
        self.HERE = Path(__file__).parent
        static_dir =   self.HERE/"review-server/static"
        template_dir = self.HERE/"review-server/templates"

        PATHS = dict(
            db = Path.home()/"code/DOCS/_dist/db/",
            media = Path.home()/"code/DOCS/_dist/_media/",
            search = Path.home()/"code/DOCS/_dist/_search/",
            static = Path.home()/"code/DOCS/_dist/static/"
        )

        # Handlers
        self._handlers += [
            # File Handlers
            (r"^/db/(.*)", tornado.web.StaticFileHandler, {"path": PATHS["db"]}),
            (r"^/_media/(.*)", tornado.web.StaticFileHandler, {"path": PATHS["media"]}),
            (r"^/_search/(.*)", tornado.web.StaticFileHandler, {"path": PATHS["search"]}),
            (r"^/static/(.*)", tornado.web.StaticFileHandler, {"path": PATHS["static"]}),
            # Catch the rest of it as an SPA
            (r"^/(.*)", MainHandler),
        ]

        # Settings
        self._settings = dict(
            debug= True,
            autoreload= True
        )


async def main():
    PORT = 8100
    ADDRESS = "localhost"
    app = MyApp()
    app.listen(PORT,address=ADDRESS)
    print(f"Running at {ADDRESS}:{PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())