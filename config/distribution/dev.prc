# What the development distribution changes.
#
# general.prc loads first and holds everything the game does the same way
# everywhere, so this file is a diff against it.

# Distribution:
distribution dev

# Audio:
audio-library-name p3openal_audio

# Art assets:
model-path ../resources

# Server:
server-version dev

# UberDOG:
generate-global-object 4688 CentralLogger
generate-global-object 4665 ClientServicesManager
generate-global-object 4681 ChatAgent
generate-global-object 4501 FriendManager
generate-global-object 4686 AvatarFriendsManager
generate-global-object 4687 PlayerFriendsManager
generate-global-object 4666 TTIFriendsManager
generate-global-object 4712 TTSpeedchatRelay
generate-global-object 4683 DistributedDeliveryManager
generate-global-object 4684 DistributedDataStoreManager
generate-global-object 4691 DistributedPartyManager
generate-global-object 4695 TTCodeRedemptionMgr
# generate-global-object 4701 GuildManager
# generate-global-object 4478 GlobalGroupTracker
# generate-global-object 4950 ZoneManager

# DC file:
dc-file astron/dclass/vanilla.dc

# Core features:
want-multiplayer #t
want-parties #t
want-achievements #f
want-grouptracker #f
want-server-browser #f

# Cog buildings:
want-cogbuildings #t
want-cogdominiums #t

# Cashbot boss:
want-resistance-dance #t

# Chat:
want-whitelist #f
want-blacklist #f

# Double progression:
want-double-progression #t

# Developer options:
want-quest-verification #t
want-heartbeat #f
want-yin-yang #t

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f

# Mod tools:
want-mods #f
