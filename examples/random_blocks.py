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
