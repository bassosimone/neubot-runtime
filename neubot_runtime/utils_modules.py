# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

""" Utils for loading tests as modules """

import logging
import os
import sys

def modprobe(rootdir, filt, context, message):
    """ Probe all modules """

    for name in os.listdir(rootdir):
        pathname = os.sep.join([rootdir, name])
        if not os.path.isdir(pathname):
            continue
        if not name.startswith("mod_"):
            continue

        logging.debug("utils_modules: early candidate: %s", name)

        initfile = os.sep.join([pathname, "__init__.py"])
        if not os.path.isfile(initfile):
            continue

        modfile = os.sep.join([pathname, "neubot_module.py"])
        if not os.path.isfile(modfile):
            continue

        logging.debug("utils_modules: good candidate: %s", name)

        if filt != None and name != filt:
            logging.debug("utils_modules: skip '%s' (filt: %s)", name, filt)
            continue

        modname = "neubot.%s.neubot_module" % name

        try:
            __import__(modname)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logging.warning("utils_modules: import error for: %s",
                            name, exc_info=1)
            continue

        logging.debug("utils_modules: import '%s'... OK", name)

        try:
            mod_load = sys.modules[modname].mod_load
        except AttributeError:
            logging.warning("utils_modules: no mod_load() in '%s'", name)
            continue

        logging.debug("utils_modules: found mod_load() in '%s'", name)

        try:
            mod_load(context, message)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logging.warning("utils_modules: mod_load() error for '%s'",
                            name, exc_info=1)
            continue

        logging.info("Loaded module '%s' for '%s' context", name, context)
