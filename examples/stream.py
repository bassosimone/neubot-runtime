#
# Copyright (c) 2010-2012, 2015
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

""" Shows how to use Neubot's stream """

from collections import deque
import getopt
import logging
import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from neubot_runtime.poller import Poller
from neubot_runtime.stream import Stream
from neubot_runtime.stream_handler import StreamHandler

class EchoStream(Stream):
    """ Stream implementing the echo protocol """

    def __init__(self, poller, parent, sock, conf):
        logging.debug("echo stream")
        Stream.__init__(self, poller, parent, sock, conf)
        self._buffer = deque()

    def connection_made(self):
        logging.debug("starting to receive data")
        self.start_recv()

    def recv_complete(self, octets):
        logging.debug("recv complete; buffering and receiving more")
        self.start_recv()
        self._buffer.append(octets)
        self._flush()

    def send_complete(self):
        logging.debug("send complete")
        self._buffer.popleft()
        self._flush()

    def _flush(self):
        """ Flush output buffer """
        if not self.send_pending and self._buffer:
            self.start_send(self._buffer[0])

class ChargenStream(Stream):
    """ Stream implementing the chargen protocol """

    def __init__(self, poller, parent, sock, conf, chunk):
        logging.debug("chargen stream")
        Stream.__init__(self, poller, parent, sock, conf)
        self._buffer = b"A" * chunk

    def connection_made(self):
        logging.debug("starting to send data")
        self.start_send(self._buffer)

    def send_complete(self):
        logging.debug("send complete; sending more data")
        self.start_send(self._buffer)

class DiscardStream(Stream):
    """ Stream implementing the discard protocol """

    def __init__(self, poller, parent, sock, conf):
        logging.debug("discard stream")
        Stream.__init__(self, poller, parent, sock, conf)

    def connection_made(self):
        logging.debug("starting to receive data")
        self.start_recv()

    def recv_complete(self, octets):
        logging.debug("recv complete; receiving more data")
        self.start_recv()

class EchoHandler(StreamHandler):
    """ Handler implementing the echo protocol """

    def __init__(self, poller):
        logging.debug("echo handler")
        StreamHandler.__init__(self, poller)

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = EchoStream(self.poller, self, sock, self.conf)
        stream.connection_made()

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

class ChargenHandler(StreamHandler):
    """ Handler implementing the chargen protocol """

    def __init__(self, poller):
        logging.debug("chargen handler")
        StreamHandler.__init__(self, poller)

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = ChargenStream(self.poller, self, sock, self.conf, 65535)
        stream.connection_made()

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

class DiscardHandler(StreamHandler):
    """ Handler implementing the discard protocol """

    def __init__(self, poller):
        logging.debug("discard handler")
        StreamHandler.__init__(self, poller)

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = DiscardStream(self.poller, self, sock, self.conf)
        stream.connection_made()

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

def main(args):
    """ Main function """
    address = "127.0.0.1"
    handler = EchoHandler
    listen = False
    port = "54321"
    noisy = logging.INFO

    try:
        options, _ = getopt.getopt(args[1:], "A:CDlp:v")
    except getopt.error:
        sys.exit("usage: example/stream.py [-CDlv] [-A address] [-p port]")
    for name, value in options:
        if name == "-A":
            address = value
        elif name == "-C":
            handler = ChargenHandler
        elif name == "-D":
            handler = DiscardHandler
        elif name == "-l":
            listen = True
        elif name == "-p":
            port = value
        elif name == "-v":
            noisy = logging.DEBUG

    logging.basicConfig(format="%(message)s", level=noisy)

    poller = Poller()
    instance = handler(poller)
    if not listen:
        instance.connect((address, port))
    else:
        instance.listen((address, port))

    poller.loop()

if __name__ == "__main__":
    main(sys.argv)
