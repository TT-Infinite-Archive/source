"""
The startup both compiled entry points share.
"""
from panda3d.core import Filename, VirtualFileSystem, loadPrcFileData
import os
import sys
import zipfile

from toontown.toonbase import ConfigFiles

PHASES = ('3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13')

DISTRIBUTION = ConfigFiles.LIVE


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


def loadPacked(paths):
    """
    Load PRC files packed into the archive the game runs from.
    """
    with zipfile.ZipFile(__loader__.archive) as archive:
        for path in paths:
            try:
                data = archive.read(path)
            except KeyError:
                sys.exit('%s carries no %s. Please run the installer again.'
                         % (os.path.basename(archive.filename), path))

            loadPrcFileData(path, data.decode('utf-8'))


def prepare(config):
    """
    Mount the phase files and load `config`.
    """
    sys.frozen = True
    sys.executable = os.path.abspath(sys.argv[0])

    root = findRoot(os.path.dirname(sys.executable))
    sys.installDirectory = root

    vfs = VirtualFileSystem.getGlobalPtr()

    vfs.chdir(Filename.fromOsSpecific(root))

    for phase in PHASES:
        multifile = Filename.fromOsSpecific(os.path.join(root, 'resources', 'phase_%s.mf' % phase))

        if not vfs.mount(multifile, '/', 0):
            sys.exit('Failed to mount %s.' % multifile)

    loadPacked(config)

    data = os.environ.get('TTI_DATA_DIRECTORY') or root

    os.makedirs(data, exist_ok=True)
    os.chdir(data)

    return root
