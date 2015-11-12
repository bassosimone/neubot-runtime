# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Shows how to use random-blocks """

import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from neubot_runtime.random_blocks import RandomBlocks

def main(args):
    """ Main function """
    # In production better to use the default rather than 80
    random_blocks = RandomBlocks("neubot_runtime", 80)
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    random_blocks.reinit()
    sys.stdout.write("---\n")
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    random_blocks.reinit()
    sys.stdout.write("---\n")
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))
    sys.stdout.write("%s\n" % random_blocks.get_block().decode("iso-8859-1"))

if __name__ == "__main__":
    main(sys.argv)
