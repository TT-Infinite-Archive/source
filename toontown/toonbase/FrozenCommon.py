"""
The startup both compiled entry points share.
"""
from panda3d.core import Filename, VirtualFileSystem, loadPrcFile
import os
import sys

PHASES = ('3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13')

DISTRIBUTION = 'live'


def findRoot(start):
    """
    Locate the install root from wherever the executable happens to sit.
    """
    directory = start

    for _ in range(6):
        # The first phase file, not the directory holding it: macOS is
        # case-insensitive
        if os.path.isfile(os.path.join(directory, 'resources', 'phase_%s.mf' % PHASES[0])):
            return directory

        parent = os.path.dirname(directory)

        if parent == directory:
            break

        directory = parent

    sys.exit('No installed resources above %s.' % start)


def prepare():
    """
    Enter the install root, mount the phase files, and load the shared config.
    """
    sys.frozen = True
    sys.executable = os.path.abspath(sys.argv[0])

    root = findRoot(os.path.dirname(sys.executable))

    os.chdir(root)

    vfs = VirtualFileSystem.getGlobalPtr()

    for phase in PHASES:
        multifile = Filename.fromOsSpecific(os.path.join(root, 'resources', 'phase_%s.mf' % phase))

        if not vfs.mount(multifile, '/', 0):
            sys.exit('Failed to mount %s.' % multifile)

    # ClientStart and both ServiceStarts load their config only under
    # __debug__, which -O removes. These are that config:
    loadPrcFile('config/general.prc')
    loadPrcFile('config/distribution/%s.prc' % DISTRIBUTION)

    return root
