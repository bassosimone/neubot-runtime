# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' An object that can be passed to the poller '''

from . import utils

# States returned by the socket model
(SUCCESS, WANT_READ, WANT_WRITE, CONNRST) = range(4)

# Reclaim stream after 300 seconds
WATCHDOG = 300

class Pollable(object):
    ''' Base class for pollable objects '''

    def __init__(self):
        self._created = utils.ticks()
        self._watchdog = WATCHDOG

    def fileno(self):
        ''' Return file descriptor number '''

    def handle_read(self):
        ''' Handle the READ event '''

    def handle_write(self):
        ''' Handle the WRITE event '''

    def handle_close(self):
        ''' Handle the CLOSE event '''

    def handle_periodic(self, timenow):
        ''' Handle the PERIODIC event '''
        return self._watchdog >= 0 and timenow - self._created > self._watchdog

    def set_timeout(self, timeo):
        ''' Set timeout of this pollable '''
        self._created = utils.ticks()
        self._watchdog = timeo
