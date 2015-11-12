#
# Copyright (c) 2010-2011, 2015
#     Nexa Center for Internet & Society, Politecnico di Torino (DAUIN)
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

''' Showing how to use http client '''

from neubot_runtime.third_party import six
from neubot_runtime.http_client import HttpClient
from neubot_runtime.http_message import HttpMessage
from neubot_runtime.poller import Poller

import getopt
import logging
import os
import sys

class ExampleHttpClient(HttpClient):
    ''' Example HTTP client '''

    def __init__(self, poller, method, uri, use_stdout):
        HttpClient.__init__(self, poller)
        self._method = method
        self._uri = uri
        self._use_stdout = use_stdout

    def connection_ready(self, stream):

        request = HttpMessage()
        if self._method == "PUT":
            fpath = self._uri.split("/")[-1]
            if not os.path.exists(fpath):
                logging.error("local file does not exist: %s", fpath)
                sys.exit(1)
            request.compose(method=self._method, uri=self._uri, keepalive=False,
                            mimetype="text/plain", body=open(fpath, "rb"))
        else:
            request.compose(method=self._method, uri=self._uri, keepalive=False)

        response = HttpMessage()
        if self._method == "GET" and not self._use_stdout:
            fpath = self._uri.split("/")[-1]
            if os.path.exists(fpath):
                logging.error("* Local file already exists: %s", fpath)
                sys.exit(1)
            response.body = open(fpath, "w")
        else:
            response.body = sys.stdout

        stream.send_request(request, response)

    def got_response_body_piece(self, response, body):
        if six.PY3:
            body = str(body, "iso-8859-1")
        response.body.write(body)

def main(args):
    ''' main() of this module '''

    method = "GET"
    use_stdout = True
    noisy = logging.INFO
    try:
        options, arguments = getopt.getopt(args[1:], "OPv")
    except getopt.error:
        sys.exit("usage: example/http_client.py [-OPv] URI")
    for name, _ in options:
        if name == "-O":
            use_stdout = False
        elif name == "-P":
            method = "PUT"
        elif name == "-v":
            noisy = logging.DEBUG
    if len(arguments) != 1:
        sys.exit("usage: example/http_client.py [-OPv] URI")
    uri = arguments[0]

    logging.basicConfig(format="%(message)s", level=noisy)
    poller = Poller()
    client = ExampleHttpClient(poller, method, uri, use_stdout)
    client.connect_uri(uri)
    poller.loop()

if __name__ == "__main__":
    main(sys.argv)
