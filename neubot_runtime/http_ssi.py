# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

'''
 Minimal Server Side Includes (SSI) implementation to help
 the development of the Web User Interface (WUI).
 The code below has been written with an healthy amound
 of prejudice^H^H^H paranoia against Unicode and attempts to
 enforce an ASCII-only policy on all the path names.
'''

import re

from . import utils_path

MAXDEPTH = 8
REGEX = '<!--#include virtual="([A-Za-z0-9./_-]+)"-->'

def ssi_open(rootdir, path, mode):
    ''' Wrapper for open() that makes security checks '''
    path = utils_path.append(rootdir, path, False)
    if not path:
        raise ValueError("ssi: Path name above root directory")
    return open(path, mode)

def ssi_split(rootdir, document, page, count):
    ''' Split the page and perform inclusion '''
    if count > MAXDEPTH:
        raise ValueError("ssi: Too many nested includes")
    include = False
    for chunk in re.split(REGEX, document):
        if include:
            include = False
            filep = ssi_open(rootdir, chunk, "rb")
            ssi_split(rootdir, filep.read(), page, count + 1)
            filep.close()
        else:
            include = True
            page.append(chunk)

def ssi_replace(rootdir, filep):
    ''' Replace with SSI the content of @filep '''
    page = []
    ssi_split(rootdir, filep.read(), page, 0)
    return "".join(page)
