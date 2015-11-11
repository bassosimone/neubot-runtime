# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' HTTP client '''

import logging

from .stream_handler import StreamHandler
from .http_client_stream import HttpClientStream
from .http_message import HttpMessage
from . import utils
from . import utils_net

class HttpClient(StreamHandler):
    ''' Manages one or more HTTP client streams '''

    def __init__(self, poller):
        StreamHandler.__init__(self, poller)
        self.host_header = ""
        self.rtt = 0

    def connect_uri(self, uri, count=1):
        ''' Connects to the given URI '''
        try:
            # Use message to parse the URI to get the endpoint...
            message = HttpMessage()
            message.compose(method="GET", uri=uri)
            endpoint = (message.address, int(message.port))
            self.host_header = utils_net.format_epnt(endpoint)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as why:
            self.connection_failed(None, why)
        else:
            self.connect(endpoint, count)

    def connection_ready(self, stream):
        ''' Invoked when the connection is ready '''

    def got_response_headers(self, stream, request, response):
        ''' Invoked when we receive response headers '''
        return True

    def got_response_body_piece(self, response, piece):
        """ Got piece of response body """

    def got_response(self, stream, request, response):
        ''' Invoked when we receive the response headers and body '''

    def connection_made(self, sock, endpoint, rtt):
        ''' Invoked when the connection is created '''
        if rtt:
            logging.debug("connect took %s", utils.time_formatter(rtt))
            self.rtt = rtt
        # If we didn't connect via connect_uri()...
        if not self.host_header:
            self.host_header = utils_net.format_epnt(endpoint)
        stream = HttpClientStream(self.poller, self, sock, self.conf)
        stream.connection_made()
        self.connection_ready(stream)
