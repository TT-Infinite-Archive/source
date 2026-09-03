"""
Entry point for a compiled build of the Toontown Infinite client.
"""
from toontown.toonbase import ConfigFiles
from toontown.toonbase.FrozenCommon import DISTRIBUTION, prepare

prepare(ConfigFiles.client(DISTRIBUTION))

import toontown.toonbase.ClientStart
