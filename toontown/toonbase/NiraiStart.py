#!/usr/bin/env python2
""""Entry point for a compiled build of Toontown Infinite."""
import __builtin__
import game_data
import argparse
from toontown.singleplayer import SinglePlayerGlobals
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
__builtin__.builtFile = 'infinite.exe'

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--district-name', help="What this AI Server's district will be named.")
args = parser.parse_args()

if args.district_name:
    import toontown.ai.ServiceStart
elif args.base_channel:
    import toontown.uberdog.ServiceStart
else:
    import toontown.toonbase.ClientStart
