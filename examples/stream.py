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

    def connection_made(self):
        logging.debug("connection made")
        self.start_recv()

    def recv_complete(self, octets):
        logging.debug("recv complete")
        self.start_recv()
        self.start_send(octets)

    def send_complete(self):
        logging.debug("send complete")

class ChargenStream(Stream):
    """ Stream implementing the chargen protocol """

    def __init__(self, poller, chunk):
        Stream.__init__(self, poller)
        self._buffer = b"A" * chunk

    def connection_made(self):
        logging.debug("connection made")
        self.start_send(self._buffer)

    def send_complete(self):
        logging.debug("send complete")
        self.start_send(self._buffer)

class DiscardStream(Stream):
    """ Stream implementing the discard protocol """

    def connection_made(self):
        logging.debug("connection made")
        self.start_recv()

    def recv_complete(self, octets):
        logging.debug("recv complete")
        self.start_recv()

class EchoHandler(StreamHandler):
    """ Handler implementing the echo protocol """

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = EchoStream(self.poller)
        stream.attach(self, sock, self.conf)

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

class ChargenHandler(StreamHandler):
    """ Handler implementing the chargen protocol """

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = ChargenStream(self.poller, 65535)
        stream.attach(self, sock, self.conf)

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

class DiscardHandler(StreamHandler):
    """ Handler implementing the discard protocol """

    def connection_made(self, sock, endpoint, rtt):
        logging.info("connection made: %s - %f", endpoint, rtt)
        stream = DiscardStream(self.poller)
        stream.attach(self, sock, self.conf)

    def connection_lost(self, stream):
        logging.info("connection lost: %s", str(stream))

def main(args):
    """ Main function """
    address = "127.0.0.1 ::1"
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
    instance.configure({})
    if not listen:
        instance.connect((address, port))
    else:
        instance.listen((address, port))

    poller.loop()

if __name__ == "__main__":
    main(sys.argv)
