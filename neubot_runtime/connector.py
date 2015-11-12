# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Internally used connector """

from .pollable import Pollable
from . import utils
from . import utils_net

class Connector(Pollable):
    """ Connects to the remote endpoint """

    def __init__(self, poller, parent, endpoint, conf):
        Pollable.__init__(self)
        self._poller = poller
        self._parent = parent
        self._timestamp = 0

        self._endpoint = endpoint
        self._sock = utils_net.connect(endpoint, conf.get("prefer_ipv6", False))
        if not self._sock:
            self._parent.connection_failed(self, None)
            return

        self._timestamp = utils.ticks()
        self._poller.set_writable(self)
        self.set_timeout(10)

    def __repr__(self):
        return "connector to %s" % str(self._endpoint)

    def fileno(self):
        return self._sock.fileno()

    def handle_write(self):
        self._poller.unset_writable(self)

        if not utils_net.isconnected(self._endpoint, self._sock):
            self._parent.connection_failed(self, None)
            return

        rtt = utils.ticks() - self._timestamp
        self._parent.connection_made(self._sock, self._endpoint, rtt)

    def handle_close(self):
        self._parent.connection_failed(self, None)
