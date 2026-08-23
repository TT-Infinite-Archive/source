# Distribution:
distribution dev

# Audio:
audio-library-name p3openal_audio

# Art assets:
model-path ../resources

# Server:
server-version dev

# developer   login screen, any username, accessLevel 500
# offline     login screen, any username, accessLevel 100
# production  no login screen; uses the launcher's launch token
accountdb-type developer

# MongoDB:
mongodb-url mongodb://localhost/game

# UberDOG:
generate-root-object #t
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

# Live account service (the website):
account-service-url 
account-service-secret 
want-game-gateway #t

# DC file:
dc-file astron/dclass/vanilla.dc

# Core features:
want-multiplayer #t
want-pets #t
want-parties #t
want-achievements #f
want-grouptracker #f
want-server-browser #f

# Safe zones:
want-safe-zones #t
want-toontown-central #t
want-donalds-dock #t
want-daisys-garden #t
want-minnies-melodyland #t
want-the-burrrgh #t
want-donalds-dreamland #t
want-goofy-speedway #t
want-outdoor-zone #t
want-golf-zone #t
want-resistance-grounds #f

# Cog headquarters:
want-cog-headquarters #t

# Cog buildings:
want-cogbuildings #t
want-cogdominiums #t

# Animated Props
zero-pause-mult 1.0

# Interactive Props
randomize-interactive-idles #t
interactive-prop-random-idles #t
interactive-prop-info #f
props-buff-battles #t
prop-and-organic-bonus-stack #f
prop-idle-pause-time 0.0

# Cashbot boss:
want-resistance-toonup #t
want-resistance-restock #t
want-resistance-dance #t

# Trolley minigames:
want-ttc-trolley #t
want-photo-game #f
want-travel-game #f

# Chat:
want-whitelist #f
want-blacklist #f

# Double progression:
want-double-progression #t

# Developer options:
show-population #f
want-instant-parties #t
want-quest-verification #t
want-heartbeat #f
want-yin-yang #t

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f

# Mod tools:
want-mods #f
