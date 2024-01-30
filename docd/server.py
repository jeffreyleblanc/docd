# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

"""
Simple http file server.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler


class RejectHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_error(403)
    def do_HEAD(self):
        self.send_error(403)

class DocdServer(HTTPServer):
    _ROOT_DIRECTORY = "/tmp"
    _ALLOWED_CLIENTS = None

    def finish_request(self, request, client_address):
        print("Request:",request)
        print("Client:",client_address)
        if self._ALLOWED_CLIENTS is not None:
            client_ip = client_address[0]
            if client_ip not in self._ALLOWED_CLIENTS:
                print("Reject!")
                # Might be a better way to do this
                RejectHandler(request,client_address,self)
                return
        self.RequestHandlerClass(
            request, client_address,self,directory=self._ROOT_DIRECTORY)

def make_server(bind_addr, port):
    return DocdServer((bind_addr,port),SimpleHTTPRequestHandler)
