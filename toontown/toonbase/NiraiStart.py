#!/usr/bin/env python2
""""Entry point for a compiled build of Toontown Infinite."""
import __builtin__
import sys

import game_data
from panda3d.core import loadPrcFileData, VirtualFileSystem, \
    ConfigVariableList, Filename, StringStream

# Hack fix for ctypes
sys.dllhandle = 0

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

# Store the deobfuscated DC file data for later use
__builtin__.dcData = game_data.deobfuscate(game_data.DC)

# __builtin__.process is automatically defined by the runtime
if process == 'client':
    import toontown.toonbase.ClientStart
elif process == 'ai':
    import toontown.ai.ServiceStart
elif process == 'uberdog':
    import toontown.uberdog.ServiceStart
