# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
Simple http file server.
"""

import argparse
from pathlib import Path
from docd.server import make_server

def main_run(args):
    try:
        bind_addr = "0.0.0.0" if args.open else "127.0.0.1"
        httpd = make_server(bind_addr,args.port)
        httpd._ROOT_DIRECTORY = args.directory
        httpd._ALLOWED_CLIENTS = args.allowed
        print(f"Running at: {bind_addr}:{args.port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("shutting down")
        httpd.shutdown()

