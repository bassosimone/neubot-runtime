#
# Copyright (c) 2010-2011, 2015
#     Nexa Center for Internet & Society, Politecnico di Torino (DAUIN),
#     and Simone Basso <bassosimone@gmail.com>.
#
# This file is part of Neubot <http://www.neubot.org/>.
#
# Neubot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Neubot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Neubot.  If not, see <http://www.gnu.org/licenses/>.
#

''' HTTP server '''

import sys
import logging

from .http_message import HttpMessage
from .http_server_stream import HttpServerStream
from .stream_handler import StreamHandler
from .poller import POLLER

class HttpServer(StreamHandler):
    ''' Manages many HTTP server connections '''

    def __init__(self, poller):
        StreamHandler.__init__(self, poller)
        self._childs = {}

    def register_child(self, child, prefix):
        ''' Register a child server object '''
        self._childs[prefix] = child

    def got_request_headers(self, stream, request):
        ''' Invoked when we got request headers '''
        for prefix, child in self._childs.items():
            if request.uri.startswith(prefix):
                try:
                    return child.got_request_headers(stream, request)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    self._on_internal_error(stream, request)
                    return False
        return True

    def process_request(self, stream, request):
        ''' Process a request and generate the response '''
        response = HttpMessage()

        if not request.uri.startswith("/"):
            response.compose(code="403", reason="Forbidden",
                             body="403 Forbidden")
            stream.send_response(request, response)
            return

        for prefix, child in self._childs.items():
            if request.uri.startswith(prefix):
                child.process_request(stream, request)
                return

        response.compose(code="403", reason="Forbidden",
                         body="403 Forbidden")
        stream.send_response(request, response)

    def got_request(self, stream, request):
        ''' Invoked when we got a request '''
        try:
            self.process_request(stream, request)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self._on_internal_error(stream, request)

    def got_request_body_piece(self, request, piece):
        """ Got piece of request body """

    @staticmethod
    def _on_internal_error(stream, request):
        ''' Generate 500 Internal Server Error page '''
        try:
            logging.error('Internal error while serving response', exc_info=1)
            response = HttpMessage()
            response.compose(code="500", reason="Internal Server Error",
                             body="500 Internal Server Error", keepalive=0)
            stream.send_response(request, response)
            stream.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pass

    def connection_made(self, sock, endpoint, rtt):
        stream = HttpServerStream(self.poller, self, sock, self.conf.copy())
        stream.connection_made()
        self.connection_ready(stream)

    def connection_ready(self, stream):
        ''' Invoked when the connection is ready '''

    def accept_failed(self, _, exception):
        logging.warning("HttpServer: accept() failed: %s", str(exception))

HTTP_SERVER = HttpServer(POLLER)
