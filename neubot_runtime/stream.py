# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Stream abstraction """

import errno
import logging
import socket

from .pollable import Pollable
from . import compat23
from . import utils_net

# Maximum amount of bytes we read from a socket
MAXBUF = 1 << 18

# Soft errors on sockets, i.e. we can retry later
SOFT_ERRORS = (errno.EAGAIN, errno.EWOULDBLOCK, errno.EINTR)

class Stream(Pollable):
    """ Stream class """

    def __init__(self, poller, parent, sock, conf):
        Pollable.__init__(self)
        self.poller = poller
        self.parent = parent
        self.conf = conf

        self.sock = sock
        self.filenum = sock.fileno()
        self.myname = utils_net.getsockname(sock)
        self.peername = utils_net.getpeername(sock)
        self.logname = str((self.myname, self.peername))
        self.eof = False
        self.rst = False

        self.close_complete = False
        self.close_pending = False
        self.recv_pending = False
        self.send_octets = None
        self.send_pending = False

        self.bytes_recv_tot = 0
        self.bytes_sent_tot = 0

        self.opaque = None
        self.atclosev = set()

    def __repr__(self):
        return "stream %s" % self.logname

    def fileno(self):
        return self.filenum

    def connection_made(self):
        """ Called when the connection is made """

    def atclose(self, func):
        """ Register function to be called at close """
        if func in self.atclosev:
            logging.warning("Duplicate atclose(): %s", func)
        self.atclosev.add(func)

    def unregister_atclose(self, func):
        """ Unregister function called at close """
        if func in self.atclosev:
            self.atclosev.remove(func)

    def connection_lost(self, exception):
        """ Called when the connection is lost """

    def close(self):
        """ Close this stream """
        self.close_pending = True
        logging.debug("called close()")
        if self.send_pending or self.close_complete:
            if self.send_pending:
                logging.debug("wait for send to complete before closing")
            return
        self.poller.close(self)

    def handle_close(self):
        if self.close_complete:
            return
        self.close_complete = True
        logging.debug("stream close... complete")

        self.connection_lost(None)
        self.parent.connection_lost(self)
        self.send_octets = None

        for func in self.atclosev:
            try:
                func(self, None)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                logging.error("close callback failed", exc_info=1)
        self.atclosev.clear()

        try:
            self.sock.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logging.error("cannot close socket", exc_info=1)

    def start_recv(self):
        """ Start async recv operation """
        if self.close_complete or self.close_pending:
            return
        if self.recv_pending:
            raise RuntimeError("recv already pending")
        self.recv_pending = True
        self.poller.set_readable(self)

    def handle_read(self):
        try:
            octets = self.sock.recv(MAXBUF)
        except (KeyboardInterrupt, SystemExit):
            raise
        except socket.error as error:
            if error.args[0] in SOFT_ERRORS:
                return
            if error.args[0] == errno.ECONNRESET:
                logging.debug("received RST (reading)")
                self.rst = True
                self.poller.close(self)
                return
            raise
        except:
            raise
        else:
            if octets:
                logging.debug("received %d bytes", len(octets))
                self.bytes_recv_tot += len(octets)
                self.recv_pending = False
                self.poller.unset_readable(self)
                self.recv_complete(octets)
                return
            logging.debug("received EOF (reading)")
            self.eof = True
            self.poller.close(self)

    def recv_complete(self, octets):
        """ Called when recv is complete """

    def start_send(self, octets):
        """ Starts async send operation """
        if self.close_complete or self.close_pending:
            return
        if self.send_pending:
            raise RuntimeError("send already pending")
        self.send_octets = octets
        self.send_pending = True
        self.poller.set_writable(self)

    def handle_write(self):
        try:
            count = self.sock.send(self.send_octets)
        except (KeyboardInterrupt, SystemExit):
            raise
        except socket.error as error:
            if error.args[0] in SOFT_ERRORS:
                return
            if error.args[0] == errno.ECONNRESET:
                logging.debug("received RST (writing)")
                self.rst = True
                self.poller.close(self)
                return
            raise
        except:
            raise
        else:
            if count > 0:
                logging.debug("sent %d bytes", count)
                self.bytes_sent_tot += count
                if count == len(self.send_octets):
                    self.send_pending = False
                    self.poller.unset_writable(self)
                    if not self.close_pending:
                        self.send_complete()
                    else:
                        logging.debug("resuming close procedure")
                        self.poller.close(self)
                    return
                if count < len(self.send_octets):
                    self.send_octets = compat23.buff(self.send_octets, count)
                    return
                raise RuntimeError("Sent more than expected")
            if count == len(self.send_octets) == 0:
                self.send_complete()
                return
            # Could the following happen?
            logging.debug("received EOF (writing)")
            self.eof = True
            self.poller.close(self)

    def send_complete(self):
        """ Called when send is complete """
