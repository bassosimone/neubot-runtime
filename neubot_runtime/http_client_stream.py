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

    def __init__(self, poller):
        ''' Initialize client stream '''
        HttpStream.__init__(self, poller)
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
