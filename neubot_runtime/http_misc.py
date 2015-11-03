#
# Copyright (c) 2010-2011, 2015
#     Nexa Center for Internet & Society, Politecnico di Torino (DAUIN),
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

''' An HTTP message '''

import urlparse

def urlsplit(uri):
    ''' Wrapper for urlparse.urlsplit() '''
    scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)
    if scheme != "http" and scheme != "https":
        raise ValueError("Unknown scheme")

    # Unquote IPv6 [<address>]:<port> or [<address>]
    if netloc.startswith('['):
        netloc = netloc[1:]
        index = netloc.find(']')
        if index == -1:
            raise ValueError("Invalid quoted IPv6 address")
        address = netloc[:index]

        port = netloc[index + 1:].strip()
        if not port:
            if scheme == 'https':
                port = "443"
            else:
                port = "80"
        elif not port.startswith(':'):
            raise ValueError("Missing port separator")
        else:
            port = port[1:]

    elif ":" in netloc:
        address, port = netloc.split(":", 1)
    elif scheme == "https":
        address, port = netloc, "443"
    else:
        address, port = netloc, "80"

    if not path:
        path = "/"
    pathquery = path
    if query:
        pathquery = pathquery + "?" + query
    return scheme, address, port, pathquery
