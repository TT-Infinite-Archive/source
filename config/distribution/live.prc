# Distribution:
distribution live

# Audio:
audio-library-name p3openal_audio

# Server:
server-version SERVER_VERSION

# Art assets:
model-path /

# DC file:
# Nirai baked the DC into the binary, so live never had to name it. Anything
# running from source, the Docker images included, does.
dc-file astron/dclass/vanilla.dc

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

# Core features:
want-multiplayer #t
want-pets #t
want-parties #t
want-achievements #f
want-grouptracker #f

# Safe zones:
want-safe-zones #t
want-minnies-melodyland #t
want-the-burrrgh #t
want-donalds-dreamland #t
want-goofy-speedway #t
want-outdoor-zone #t
want-golf-zone #t

# Cog headquarters:
want-cog-headquarters #t

# Cog buildings:
want-cogbuildings #t
want-cogdominiums #t

# Sellbot boss:
disable-sos-card 91917
disable-sos-card 91918

# Trolley minigames:
want-ttc-trolley #t
want-photo-game #f
want-travel-game #f

# Chat:
want-whitelist #t
want-blacklist #t

# Developer options:
want-yin-yang #t
want-phone-quest #f
want-heartbeat #f

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f

# Mod tools:
want-mods #f