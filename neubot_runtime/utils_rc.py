# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' Configuration file utils '''

import os
import shlex
import sys

def parse(path=None, iterable=None):
    ''' Parse configuration file or iterable '''

    if path and iterable:
        raise ValueError('Both path and iterable are not None')
    elif path:
        if not os.path.isfile(path):
            return {}
        iterable = open(path, 'rb')
    elif iterable:
        path = '<cmdline>'
    else:
        return {}

    conf = {}
    lineno = 0
    for line in iterable:
        lineno += 1
        tokens = shlex.split(line, True)
        if not tokens:
            continue

        # Support both key=value and 'key value' syntaxes
        if len(tokens) == 1 and '=' in tokens[0]:
            tokens = tokens[0].split('=', 1)
        if len(tokens) != 2:
            raise ValueError('%s:%d: Invalid line' % (path, lineno))

        name, value = tokens
        conf[name] = value

    return conf

def parse_safe(path=None, iterable=None):
    ''' Parse configuration file or iterable (safe) '''
    try:
        return parse(path, iterable)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        exc = sys.exc_info()[1]
        error = str(exc)
        sys.stderr.write('WARNING: utils_rc: %s\n' % error)
        return {}
