# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' Random body for HTTP code '''

class RandomBody(object):

    '''
     This class implements a minimal file-like interface and
     employs the random number generator to create the content
     returned by its read() method.
    '''

    def __init__(self, random_blocks, total):
        ''' Initialize random body object '''
        self._random_blocks = random_blocks
        self._total = total

    def read(self, want=None):
        ''' Read up to @want bytes '''
        if not want:
            want = self._total
        amt = min(self._total, min(want, self._random_blocks.blocksiz))
        if amt:
            self._total -= amt
            return self._random_blocks.get_block()[:amt]
        else:
            return b''

    def seek(self, offset=0, whence=0):
        ''' Seek stub '''

    def tell(self):
        ''' Tell the amounts of bytes left '''
        return self._total
