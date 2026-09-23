"""
Which PRC files are loaded for a given instance of the game.
"""
from panda3d.core import loadPrcFile
import sys


GENERAL = 'config/general.prc'
CLIENT = 'config/client.prc'
SERVER = 'config/server.prc'
LIVE = 'live'
DEV = 'dev'
HOST = 'host'


def distribution(name):
    return 'config/distribution/%s.prc' % name


def client(name=LIVE):
    return (GENERAL, CLIENT, distribution(name))


def server(name=LIVE, role=None):
    return (GENERAL, distribution(name),
            SERVER, distribution('%s-server' % (role or name)))


# What a --distribution may be. `host` is not a distribution. it is
# `live` with the server config swapped
CHOICES = (DEV, LIVE, HOST)


def serverFor(name):
    if name == HOST:
        return server(LIVE, HOST)

    return server(name)


# Overlays that belong to no distribution:
OVERLAYS = 'config/holidays'


def load(paths):
    for path in paths:
        if loadPrcFile(path) is None:
            sys.exit(
                'Missing config file: %s\n'
                'Paths are relative to the install root. If the file is not '
                'there, the install is incomplete. Please run the installer '
                'again.' % path)
