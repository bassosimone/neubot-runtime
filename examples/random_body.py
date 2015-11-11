# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Shows how to use random-body """

import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from neubot_runtime.random_blocks import RandomBlocks
from neubot_runtime.random_body import RandomBody

def main(args):
    """ Main function """
    random_blocks = RandomBlocks("neubot_runtime")
    random_body = RandomBody(random_blocks, 1024)
    sys.stdout.write("tell: %d\n" % random_body.tell())
    while True:
        data = random_body.read(64)
        if not data:
            break
        sys.stdout.write("%s\n" % data.decode("iso-8859-1"))

if __name__ == "__main__":
    main(sys.argv)
