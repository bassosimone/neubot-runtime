# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' HTTP server '''

import sys
import logging

from .http_message import HttpMessage
from .http_server_stream import HttpServerStream
from .stream_handler import StreamHandler
from .poller import POLLER

class HttpServerBase(StreamHandler):
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

class HttpServer(HttpServerBase):

    def got_request_body_piece(self, request, piece):
        request.body.write(piece)

HTTP_SERVER = HttpServer(POLLER)
