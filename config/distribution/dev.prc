# Distribution:
distribution dev

# Audio:
audio-library-name p3openal_audio

# Art assets:
model-path ../resources

# Server:
server-version dev
shard-low-pop 25
shard-mid-pop 50
accountdb-type developer
min-access-level 600

# MongoDB:
mongodb-url mongodb://localhost/game

# UberDOG:
generate-root-object #t
generate-global-object 4665 ClientServicesManager
generate-global-object 4681 ChatAgent
generate-global-object 4666 TTIFriendsManager
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

# DClass files (in reverse order):
dc-file astron/dclass/toon.dc
dc-file astron/dclass/otp.dc

# Core features:
want-multiplayer #f
want-pets #f
want-parties #f
want-achievements #f
want-grouptracker #f
want-suit-planners #t

# Double progression:
want-double-progression #t

# Chat:
want-whitelist #f
want-blacklist #f

# Cashbot boss:
want-resistance-toonup #t
want-resistance-restock #t
want-resistance-dance #t

# Developer options:
show-population #f
force-skip-tutorial #t
want-instant-parties #t
want-quest-verification #t

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f

# Safe zones:
want-safe-zones #t
want-toontown-central #t
want-donalds-dock #t
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

# Heartbeat
want-heartbeat #f

notify-level-TownBattle debug
notify-level-GagInventoryGui debug
notify-level-DistributedBattleAI debug
notify-level-DistributedBattle debug
notify-level-ChooseAvatarPanel debug
notify-level-GagInventoryBase debug
notify-level-GagInventory debug
