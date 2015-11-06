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
