#!/usr/bin/env python2
""""Entry point for a compiled build of Toontown Infinite."""
import __builtin__
import game_data
import sys
import _psutil_windows
from panda3d.core import loadPrcFileData, VirtualFileSystem, \
    ConfigVariableList, Filename, StringStream

for i, config in enumerate(game_data.CONFIG):
    name = 'game_data config page #' + str(i)
    loadPrcFileData(name, game_data.deobfuscate(config))

# Because the VFS has already been initialized, it hasn't loaded the mount
# directives defined in the game_data config pages. Therefore, we must force it
# to do so manually:
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
    mountFile = Filename(mountFile)
    mountFile.makeAbsolute()
    mountPoint = Filename(mountPoint)
    vfs.mount(mountFile, mountPoint, 0)

__builtin__.dcStream = StringStream(game_data.deobfuscate(game_data.DC))
__builtin__.builtFile = 'infinite'


class PsutilHook:
    def find_module(self, fullname, path):
        if fullname == 'psutil._psutil_windows':
            return self

    def load_module(self, fullname):
        if fullname == 'psutil._psutil_windows':
            return _psutil_windows


sys.meta_path.append(PsutilHook())

import toontown.toonbase.ClientStart
