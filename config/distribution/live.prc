# Distribution:
distribution live

# Server:
server-version SERVER_VERSION
accountdb-type production

# Temporary configuration for Alpha
access-level-clamp 100 700

# MongoDB:
mongodb-url mongodb://localhost/game

# RPC:
want-rpc-server #f
rpc-server-endpoint http://localhost:8080/

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
generate-global-object 4695 TTCodeRedemptionMgr
generate-global-object 4477 GlobalPartyManager
generate-global-object 4683 DistributedDeliveryManager
# generate-global-object 4701 GuildManager
# generate-global-object 4478 GlobalGroupTracker
generate-global-object 4901 MegaInvasionManager

# RPC:
want-rpc-server #f
rpc-server-endpoint http://localhost:8080/

# Web API:
want-web-api #f
web-api-endpoint https://localhost:8000/api/
web-api-token invalid

# Core features:
want-kaldron-network #f
want-multiplayer #t
want-pets #f
want-parties #f
want-achievements #f
want-grouptracker #f

# Safe zones:
want-safe-zones #t
want-toontown-central #t
want-donalds-dock #f
want-daisys-garden #f
want-minnies-melodyland #f
want-the-burrrgh #f
want-donalds-dreamland #f
want-goofy-speedway #f
want-outdoor-zone #f
want-golf-zone #f
want-resistance-grounds #f

# Cog headquarters:
want-cog-headquarters #f

# Cog buildings:
want-cogbuildings #f
want-cogdominiums #f

# Sellbot boss:
disable-sos-card 91917
disable-sos-card 91918

# Trolley minigames:
want-ttc-trolley #t
want-photo-game #f
want-travel-game #f

# Chat:
want-whitelist #f
want-blacklist #f

# Developer options:
want-yin-yang #f
force-skip-tutorial #t
show-population #f
want-phone-quest #f
want-heartbeat #f

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f
want-dev-debug #f

# Safezone interactables:
want-ttc-jukebox #t

# Mod tools:
want-mods #f