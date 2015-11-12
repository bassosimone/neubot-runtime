# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' POSIX utils '''

import errno
import logging
import os.path
import pwd
import signal
import sys
import time

# For python3 portability
MODE_755 = int('755', 8)
MODE_644 = int('644', 8)
MODE_022 = int('022', 8)

def is_running(pid):
    ''' Returns true if PID is running '''
    # Note: fails when you are not permitted to kill PID
    running = True
    try:
        os.kill(pid, 0)
    except OSError:
        why = sys.exc_info()[1]
        if why[0] != errno.ESRCH:
            raise
        running = False
    return running

def terminate_process(pid):
    ''' Terminate process and return success/failure '''
    if not is_running(pid):
        logging.debug('utils_posix: process %d is not running', pid)
        return True
    logging.debug('utils_posix: sending %d the TERM signal', pid)
    os.kill(pid, signal.SIGTERM)
    time.sleep(1)
    if not is_running(pid):
        logging.debug('utils_posix: process %d terminated', pid)
        return True
    logging.debug('utils_posix: sending %d the KILL signal', pid)
    os.kill(pid, signal.SIGKILL)
    time.sleep(1)
    if not is_running(pid):
        logging.debug('utils_posix: process %d terminated', pid)
        return True
    return False

def daemonize(pidfile=None, sighandler=None):

    '''
     Perform the typical steps to become a daemon.

     In detail:

     1. run in the background:

         1.1. detach from the current shell;

         1.2. become a session leader;

         1.3. ignore SIGINT;

         1.4. detach from the current session;

     2. redirect stdio to /dev/null;

     3. chdir to rootdir;

     4. ignore SIGPIPE;

     5. (over)write pidfile;

     6. install SIGTERM and SIGHUP handler.

     Assumes that logging.debug() and other logging functions are
     writing messages on the system log.

     (Over)writes the pidfile unconditionally.  Fails if it's not
     possible to write it.
    '''

    #
    # In summer 2011 I verified that the first chunk of this function matches
    # loosely the behavior of OpenBSD daemon(3).  What is missing here is
    # setlogin(2), which is not available through python's standard library.
    # In January 2013 I further modified the code to match Unix Network
    # Programming vol. 1 III ed. pagg. 368-369.
    #
    # Note: the code below MUST use os._exit() (as opposed to sys.exit())
    # because the latter raises an exception that may be caught.
    #

    logging.debug('utils_posix: detach from the current shell')
    if os.fork() > 0:
        os._exit(0)

    logging.debug('utils_posix: become a session leader')
    os.setsid()

    #
    # "when the session leader terminates (the first child), all
    #  processes in the session (the second child) receive the
    #  SIGHUP signal" (UNP pag. 369)
    #
    logging.debug('utils_posix: ignore SIGINT')
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    logging.debug('utils_posix: detach from the current session')
    if os.fork() > 0:
        os._exit(0)

    logging.debug('utils_posix: redirect stdio to /dev/null')
    for fdesc in range(3):
        os.close(fdesc)
    # Unix Network Programming opens stdin as readonly
    os.open('/dev/null', os.O_RDONLY)
    os.open('/dev/null', os.O_RDWR)
    os.open('/dev/null', os.O_RDWR)

    logging.debug('utils_posix: chdir() to "/"')
    os.chdir('/')

    # Note: python already ignores SIGPIPE by default, this is just for
    # the sake of writing correct daemonizing code.
    logging.debug('utils_posix: ignore SIGPIPE')
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

    if pidfile:
        logging.debug('utils_posix: write pidfile: "%s"', pidfile)
        old_umask = os.umask(MODE_022)
        filep = open(pidfile, 'w')
        filep.write('%d\n' % os.getpid())
        filep.close()
        os.umask(old_umask)

    if sighandler:
        logging.debug('utils_posix: install SIGTERM and SIGHUP handler')
        signal.signal(signal.SIGTERM, sighandler)
        signal.signal(signal.SIGHUP, sighandler)

def remove_pidfile(pidfile):
    ''' Removes the pidfile '''
    try:
        os.unlink(pidfile)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        pass

def chuser(passwd):

    '''
     Change user (group) to `passwd.pw_uid` (`passwd.pw_gid`) and set a bare
     environement for the new user.  This function is mainly used to drop root
     privileges, but can also be used to sanitize the privileged daemon's
     environment.

     More in detail, this function will:

     1. set the umask to 022;

     2. change group ID to `passwd.pw_gid`;

     3. set minimal supplementary groups;

     4. change user ID to `passwd.pw_uid`;

     5. purify environment.

    '''

    #
    # In summer 2011 I checked that this function does more or less the same
    # steps of OpenBSD setusercontext(3) and launchd(8).  For dropping
    # privileges I try to follow the guidelines established by Chen, et al.,
    # in their 'Setuid Demystified' work:
    #
    # > Since setresuid has a clear semantics and is able to set each user ID
    # > individually, it should always be used if available.  Otherwise, to set
    # > only the effective uid, seteuid(new euid) should be used; to set all
    # > three user IDs, setreuid(new uid, new uid) should be used.
    #

    logging.debug('utils_posix: set umask 022')
    os.umask(MODE_022)

    logging.debug('utils_posix: change gid to %d', passwd.pw_gid)
    if hasattr(os, 'setresgid'):
        os.setresgid(passwd.pw_gid, passwd.pw_gid, passwd.pw_gid)
    elif hasattr(os, 'setregid'):
        os.setregid(passwd.pw_gid, passwd.pw_gid)
    else:
        raise RuntimeError('utils_posix: cannot drop group privileges')

    logging.debug('utils_posix: set minimal supplementary groups')
    os.setgroups([passwd.pw_gid])

    logging.debug('utils_posix: change uid to %d', passwd.pw_uid)
    if hasattr(os, 'setresuid'):
        os.setresuid(passwd.pw_uid, passwd.pw_uid, passwd.pw_uid)
    elif hasattr(os, 'setreuid'):
        os.setreuid(passwd.pw_uid, passwd.pw_uid)
    else:
        raise RuntimeError('utils_posix: cannot drop user privileges')

    #
    # If putenv() and unsetenv() are available, the following code should
    # reflect changes in os.environ to the environment (see Lib/os.py).
    # I cannot use os.environ.clear() because it did not cleared the 'real'
    # environ in Python 2.5.  I cannot replace the environment with a
    # dict because the latter does not automatically propagate changes
    # to the 'real' environment.
    #
    logging.debug('utils_posix: purify environ')
    for name in list(os.environ.keys()):
        del os.environ[name]
    os.environ.update({
        "HOME": "/",
        "LOGNAME": passwd.pw_name,
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "TMPDIR": "/tmp",
        "USER": passwd.pw_name,
    })

def getpwnam(uname):
    ''' Get password database entry by name '''
    # Wrapper that reports a better error message
    try:
        passwd = pwd.getpwnam(uname)
    except KeyError:
        raise RuntimeError('utils_posix: getpwnam(): "%s": no such user' %
                           uname)
    else:
        logging.debug('utils_posix: getpwnam(): %s/%d/%d', passwd.pw_name,
                      passwd.pw_uid, passwd.pw_gid)
        return passwd

def mkdir_idempotent(curpath, uid=None, gid=None):
    ''' Idempotent mkdir with 0755 permissions'''

    if not os.path.exists(curpath):
        os.mkdir(curpath, MODE_755)
    elif not os.path.isdir(curpath):
        raise RuntimeError('%s: Not a directory' % curpath)

    if uid is None:
        uid = os.getuid()
    if gid is None:
        gid = os.getgid()

    os.chown(curpath, uid, gid)
    os.chmod(curpath, MODE_755)

def touch_idempotent(curpath, uid=None, gid=None):
    ''' Idempotent touch with 0644 permissions '''

    if not os.path.exists(curpath):
        os.close(os.open(curpath, os.O_WRONLY|os.O_CREAT
                         |os.O_APPEND, MODE_644))
    elif not os.path.isfile(curpath):
        raise RuntimeError('%s: Not a file' % curpath)

    if uid is None:
        uid = os.getuid()
    if gid is None:
        gid = os.getgid()

    os.chown(curpath, uid, gid)
    os.chmod(curpath, MODE_644)
