#
# Buffer / memoryview, urlparse
# Written by Simone Basso
#

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    def buff(string, offset, size=None):
        if not size:
            size = len(string)
        return memoryview(string)[offset:offset + size]

    import urllib.parse as urlparse
    from collections import OrderedDict

    def bytes_to_string(octets, encoding):
        return str(octets, encoding)

    def bytes_to_string_safe(octets, encoding):
        return str(octets, encoding, errors='ignore')

else:
    def buff(string, offset, size=None):
        if not size:
            size = len(string)
        return buffer(string, offset, size)

    import urlparse
    from .third_party.ordered_dict import OrderedDict

    def bytes_to_string(octets, encoding):
        return octets

    def bytes_to_string_safe(octets, encoding):
        return octets
