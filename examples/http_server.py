# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' HTTP server '''

import getopt
import os
import sys
import logging

if __name__ == "__main__":
    sys.path.insert(0, ".")

from neubot_runtime.third_party import six
from neubot_runtime.http_server import HttpServer
from neubot_runtime.http_message import HttpMessage
from neubot_runtime.poller import Poller
from neubot_runtime import utils
from neubot_runtime import utils_path

class ServeFilesystem(HttpServer):
    ''' Servers files on the local filesystem '''

    def __init__(self, poller, rootdir):
        ''' Initialize the HTTP server '''
        HttpServer.__init__(self, poller)
        self._rootdir = rootdir

    @staticmethod
    def _emit_error(stream, request, response, code, reason):
        """ Emit HTTP error """
        body = "%s %s" % (code, reason)
        body = body.encode("iso-8859-1")
        response.compose(code=code, reason=reason, body=body)
        stream.send_response(request, response)

    def process_request(self, stream, request):
        response = HttpMessage()

        if not request.uri.startswith("/"):
            self._emit_error(stream, request, response, "403", "Forbidden")
            return

        if not self._rootdir:
            self._emit_error(stream, request, response, "403", "Forbidden")
            return

        if '?' in request.uri:
            request_uri = request.uri.split('?')[0]
        else:
            request_uri = request.uri

        fullpath = utils_path.append(self._rootdir, request_uri, True)
        if not fullpath:
            self._emit_error(stream, request, response, "403", "Forbidden")
            return

        try:
            filep = open(fullpath, "rb")
        except (IOError, OSError):
            self._emit_error(stream, request, response, "404", "Not Found")
            return

        response.compose(code="200", reason="Ok", body=filep,
                         mimetype="text/plain")
        if request.method == "HEAD":
            utils.safe_seek(filep, 0, os.SEEK_END)
        stream.send_response(request, response)

    def got_request_body_piece(self, request, body):
        if six.PY3:
            body = str(body, "iso-8859-1")
        request.body.write(body)

def main(args):
    ''' main() function of this module '''
    rootdir = "."
    noisy = logging.INFO
    try:
        options, _ = getopt.getopt(args[1:], "d:v")
    except getopt.error:
        sys.exit("usage: examples/http_server.py [-v] [-d rootdir]")
    for name, value in options:
        if name == "-d":
            rootdir = value
        elif name == "-v":
            noisy = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=noisy)
    poller = Poller()
    server = ServeFilesystem(poller, rootdir)
    server.listen(("127.0.0.1", 8080))
    poller.loop()

if __name__ == "__main__":
    main(sys.argv)
