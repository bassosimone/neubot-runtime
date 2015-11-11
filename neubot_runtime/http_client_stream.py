# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' HTTP client stream '''

import collections
import logging

from .http_stream import HttpStream
from .http_stream import ERROR
from .http_misc import nextstate
from .http_message import HttpMessage
from . import utils

class HttpClientStream(HttpStream):
    ''' Specializes HttpStream and implements the client
        side of an HTTP channel '''

    def __init__(self, poller, parent, socket, conf):
        HttpStream.__init__(self, poller, parent, socket, conf)
        self._requests = collections.deque()

    def send_request(self, request, response=None):
        ''' Sends a request '''
        self._requests.append(request)
        if not response:
            response = HttpMessage()
        request.response = response
        self.send_message(request)

    def got_first_line(self, protocol, code, reason):
        if protocol not in ("HTTP/1.0", "HTTP/1.1"):
            raise RuntimeError
        response = self._requests[0].response
        response.protocol = protocol
        response.code = code
        response.reason = reason

    def got_header(self, key, value):
        response = self._requests[0].response
        response[key] = value

    def got_end_of_headers(self):
        request = self._requests[0]
        if not self.parent.got_response_headers(self, request,
                                                request.response):
            return ERROR, 0
        return nextstate(request, request.response)

    def got_piece(self, piece):
        response = self._requests[0].response
        self.parent.got_response_body_piece(response, piece)

    def got_end_of_body(self):
        request = self._requests.popleft()
        utils.safe_seek(request.response.body, 0)
        request.response.prettyprintbody("<")
        self.parent.got_response(self, request, request.response)
        if (request["connection"] == "close" or
                request.response["connection"] == "close"):
            logging.debug("honoring 'connection: close' header")
            self.close()
