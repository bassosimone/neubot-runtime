# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' Generate random data blocks for the tests '''

#
# This code is inspired by code published on the blog
# of Jesse Noller <http://bit.ly/irj8je>.
#

import collections
import os.path
import random

from .third_party.six import PY3

# Maximum depth
MAXDEPTH = 16

# Size of a block
BLOCKSIZE = 262144

def _listdir(curdir, vector, depth):
    ''' Make a list of all the files in a given directory
        up to a certain depth '''

    if depth > MAXDEPTH:
        return

    for entry in os.listdir(curdir):
        entry = os.path.join(curdir, entry)
        if os.path.isdir(entry):
            _listdir(entry, vector, depth + 1)
        elif os.path.isfile(entry):
            vector.append(entry)

def _create_base_block(path, length):
    ''' Create a base block of length @length '''

    base_block = collections.deque()

    files = []
    _listdir(path, files, 0)
    random.shuffle(files)

    for fpath in files:
        fileptr = open(fpath, 'rb')
        content = fileptr.read()
        words = content.split()

        for word in words:
            amount = min(len(word), length)
            word = word[:amount]
            wordlist = list(word)
            random.shuffle(wordlist)

            if PY3:
                base_block.append(bytes(wordlist))
            else:
                base_block.append(b''.join(wordlist))

            length -= amount
            if length <= 0:
                break

        if length <= 0:
            break

    return base_block

def _block_generator(path, size):
    ''' Generator that returns blocks '''

    block = _create_base_block(path, size)
    while True:
        block.rotate(random.randrange(4, 16))
        yield b''.join(block)

class RandomBlocks(object):
    ''' Generate blocks randomly shuffling a base block '''

    def __init__(self, path, size=BLOCKSIZE):
        ''' Initialize random blocks generator '''
        self._generator = _block_generator(path, size)
        self._path = path
        self.blocksiz = size

    def reinit(self):
        ''' Reinitialize the generator '''
        self._generator = _block_generator(self._path, self.blocksiz)

    def get_block(self):
        ''' Return a block of data '''
        return next(self._generator)
