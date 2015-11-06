#
# Copyright (c) 2011, 2015
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

''' HTTP stream '''

from collections import deque
import logging

from .stream import MAXBUF
from .stream import Stream

from .http_states import BOUNDED
from .http_states import UNBOUNDED
from .http_states import CHUNK
from .http_states import CHUNK_END
from .http_states import FIRSTLINE
from .http_states import HEADER
from .http_states import CHUNK_LENGTH
from .http_states import TRAILER
from .http_states import ERROR

from .third_party import six

# Maximum allowed line length
MAXLINE = 1 << 15

# receiver state names
STATES = ("IDLE", "BOUNDED", "UNBOUNDED", "CHUNK", "CHUNK_END", "FIRSTLINE",
          "HEADER", "CHUNK_LENGTH", "TRAILER", "ERROR")

#
# When messages are not bigger than SMALLMESSAGE we join headers
# and body in a single buffer and we send that buffer.  If the buffer
# happens to be very small, it might fit a single L2 packet.
#
SMALLMESSAGE = 8000

class HttpStream(Stream):
    ''' HTTP stream '''

    def __init__(self, poller, parent, sock, conf):
        Stream.__init__(self, poller, parent, sock, conf)
        self._incoming = []
        self._state = FIRSTLINE
        self._left = 0
        self._outgoing = deque()

    def connection_made(self):
        logging.debug("now ready to read http messages")
        self.start_recv()

    def connection_lost(self, _):
        # it's possible for body to be `up to end of file`
        if self.eof and self._state == UNBOUNDED:
            self.got_end_of_body()
        self._incoming = None

    def send_message(self, message, smallmessage=SMALLMESSAGE):
        ''' Send a message '''
        if message.length >= 0 and message.length <= smallmessage:
            logging.debug("sending small http message")
            vector = []
            vector.append(message.serialize_headers().read())
            body = message.serialize_body()
            if hasattr(body, 'read'):
                vector.append(body.read())
            else:
                vector.append(body)
            data = b"".join(vector)
            self._outgoing.append(data)
        else:
            logging.debug("sending ordinary http message")
            self._outgoing.append(message.serialize_headers())
            self._outgoing.append(message.serialize_body())
        self._flush()

    def send_complete(self):
        logging.debug("send completed")
        self._outgoing.popleft()
        self._flush()

    def _flush(self):
        """ Flush outgoing queue """
        while not self.send_pending and self._outgoing:
            octets = self._outgoing[0]
            if hasattr(octets, 'read'):
                octets = octets.read()
                if octets:
                    self._outgoing.appendleft(octets)
                    self.start_send(octets)
                    logging.debug("sending data read from file")
                    continue
                self._outgoing.popleft()
                continue
            self.start_send(octets)
            logging.debug("sending buffered data")
            continue

    def recv_complete(self, data):
        logging.debug("processing incoming http data...")

        # merge with previous fragments (if any)
        if self._incoming:
            logging.debug("merging new data with previous data")
            self._incoming.append(data)
            data = b"".join(self._incoming)
            del self._incoming[:]

        # consume the current fragment
        offset = 0
        length = len(data)
        logging.debug("the current fragment is %d bytes", length)
        while length > 0:

            # when we know the length we're looking for a piece
            if self._left > 0:
                logging.debug("looking for %d more bytes", self._left)
                count = min(self._left, length)
                logging.debug("capping bytes to %d", count)
                piece = six.buff(data, offset, count)
                logging.debug("found %d-bytes piece", len(piece))
                self._left -= count
                offset += count
                length -= count
                self._got_piece(piece)

            # otherwise we're looking for the next line
            elif self._left == 0:
                index = data.find(b"\n", offset)
                if index == -1:
                    if length > MAXLINE:
                        raise RuntimeError("Line too long")
                    break
                index = index + 1
                line = data[offset:index]
                length -= (index - offset)
                logging.debug("found %d-bytes line", index - offset)
                offset = index
                self._got_line(line.decode("iso-8859-1"))

            # robustness
            else:
                raise RuntimeError("Left become negative")

            # robustness (was the connection closed by callback?)
            if self.close_complete or self.close_pending:
                logging.debug("close() was called, stop http data processing")
                return

        # keep the eventual remainder for later
        if length > 0:
            logging.debug("not all data was processed")
            remainder = data[offset:]
            self._incoming.append(remainder)

        # get the next fragment
        self.start_recv()
        logging.debug("processing incoming http data... done")

    def _got_line(self, line):
        ''' We've got a line... what do we do? '''

        if self._state == FIRSTLINE:
            line = line.strip()
            logging.debug("< %s", line)
            vector = line.split(None, 2)
            self.got_first_line(vector[0], vector[1], vector[2])
            self._state = HEADER

        elif self._state == HEADER:
            if line[0] in (" ", "\t"):
                raise RuntimeError("Not handling continuation headers")
            line = line.strip()
            if line:
                logging.debug("< %s", line)
                index = line.find(":")
                if index >= 0:
                    key, value = line.split(":", 1)
                    self.got_header(key.lower().strip(), value.strip())
                else:
                    raise RuntimeError("Invalid header line")
            else:
                logging.debug("<")
                self._state, self._left = self.got_end_of_headers()
                if self._state == ERROR:
                    # allow upstream to filter out unwanted requests
                    self.close()
                elif self._state == FIRSTLINE:
                    # this is the case of an empty body
                    self.got_end_of_body()

        elif self._state == CHUNK_LENGTH:
            vector = line.split()
            if vector:
                length = int(vector[0], 16)
                if length < 0:
                    raise RuntimeError("Negative chunk-length")
                elif length == 0:
                    self._state = TRAILER
                else:
                    self._left = length
                    self._state = CHUNK
            else:
                raise RuntimeError("Invalid chunk-length line")

        elif self._state == CHUNK_END:
            if line.strip():
                raise RuntimeError("Invalid chunk-end line")
            else:
                self._state = CHUNK_LENGTH

        elif self._state == TRAILER:
            if not line.strip():
                self._state = FIRSTLINE
                self.got_end_of_body()
            else:
                # Ignoring trailers
                pass

        else:
            raise RuntimeError("Not expecting a line")

    def _got_piece(self, piece):
        ''' We've got a piece... what do we do? '''

        if self._state == BOUNDED:
            logging.debug("got piece of bounded body")
            self.got_piece(piece)
            if self._left == 0:
                self._state = FIRSTLINE
                self.got_end_of_body()

        elif self._state == UNBOUNDED:
            logging.debug("got piece of unbounded body")
            self.got_piece(piece)
            self._left = MAXBUF

        elif self._state == CHUNK:
            logging.debug("got piece of chunked body")
            self.got_piece(piece)
            if self._left == 0:
                self._state = CHUNK_END

        else:
            raise RuntimeError("Not expecting a piece")

    def got_first_line(self, first, second, third):
        ''' Got the request line '''

    def got_header(self, key, value):
        ''' Got an header '''

    def got_end_of_headers(self):
        ''' Got the end of headers '''

    def got_piece(self, piece):
        ''' Got a piece of the body '''

    def got_end_of_body(self):
        ''' Got the end of the body '''

    def message_sent(self):
        ''' The message was sent '''
