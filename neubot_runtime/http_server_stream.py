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

''' HTTP server stream '''

import time
import logging

from .http_states import ERROR
from .http_message import HttpMessage
from .http_misc import nextstate
from .http_stream import HttpStream

from . import utils

#
# 3-letter abbreviation of month names.
# We use our abbreviation because we don't want the
# month name to depend on the locale.
# Note that Python tm.tm_mon is in range [1,12].
#
MONTH = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec",
]

class HttpServerStream(HttpStream):
    ''' Specializes HttpStream to implement the server-side
        of an HTTP channel '''

    def __init__(self, poller):
        HttpStream.__init__(self, poller)
        self.response_rewriter = lambda req, res: None
        self._request = None

    def got_first_line(self, method, uri, protocol):
        if protocol not in ("HTTP/1.0", "HTTP/1.1"):
            raise RuntimeError
        self._request = HttpMessage(method=method, uri=uri, protocol=protocol)

    def got_header(self, key, value):
        self._request[key] = value

    def got_end_of_headers(self):
        if not self.parent.got_request_headers(self, self._request):
            return ERROR, 0
        return nextstate(self._request)

    def got_piece(self, piece):
        self.parent.got_request_body_piece(self._request, piece)

    def got_end_of_body(self):
        utils.safe_seek(self._request.body, 0)
        self._request.prettyprintbody("<")
        self.parent.got_request(self, self._request)
        self._request = None

    def send_response(self, request, response):
        ''' Send a response to the client '''

        self.response_rewriter(request, response)

        if request['connection'] == 'close' or request.protocol == 'HTTP/1.0':
            del response['connection']
            response['connection'] = 'close'

        self.send_message(response)

        if response['connection'] == 'close':
            self.close()

        address = self.peername[0]
        now = time.gmtime()
        timestring = "%02d/%s/%04d:%02d:%02d:%02d -0000" % (
            now.tm_mday, MONTH[now.tm_mon], now.tm_year, now.tm_hour,
            now.tm_min, now.tm_sec)
        requestline = request.requestline
        statuscode = response.code

        nbytes = "-"
        if response["content-length"]:
            nbytes = response["content-length"]
            if nbytes == "0":
                nbytes = "-"

        logging.info("%s - - [%s] \"%s\" %s %s", address, timestring,
                     requestline, statuscode, nbytes)
