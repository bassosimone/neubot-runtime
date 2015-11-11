# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Stream handler class """

from .connector import Connector
from .listener import Listener
from . import utils_net

class StreamHandler(object):
    """ Handle many streams at once """

    def __init__(self, poller):
        self.poller = poller
        self.conf = {}

    def configure(self, conf):
        """ Configure this object """
        self.conf = conf

    def listen(self, endpoint):
        """ Listen to the specified endpoint """
        sockets = utils_net.listen(endpoint)
        if not sockets:
            self.bind_failed(endpoint)
            return
        for sock in sockets:
            Listener(self.poller, self, sock, endpoint)

    def bind_failed(self, epnt):
        """ Called when bind() failed """

    def started_listening(self, listener):
        """ Called when we started listening """

    def accept_failed(self, listener, exception):
        """ Called when accept fails """

    def connect(self, endpoint, count=1):
        """ Connect to the remote endpoint """
        if count != 1:
            raise NotImplementedError
        Connector(self.poller, self, endpoint, self.conf)

    def connection_failed(self, connector, exception):
        """ Called when a connect attempt failed """

    def started_connecting(self, connector):
        """ Called when connection is in progress """

    def connection_made(self, sock, endpoint, rtt):
        """ Called when a connection attempt succeeded """

    def connection_lost(self, stream):
        """ Called when a connection is lost """
