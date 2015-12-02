# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' Showing how to use http client '''

import getopt
import logging
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from neubot_runtime.third_party import six
from neubot_runtime.http_client import HttpClient
from neubot_runtime.http_message import HttpMessage
from neubot_runtime.poller import Poller

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
            response.body = open(fpath, "wb")
        else:
            if six.PY3:
                response.body = sys.stdout.buffer
            else:
                response.body = sys.stdout

        stream.send_request(request, response)

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
