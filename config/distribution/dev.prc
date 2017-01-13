# Distribution:
distribution dev

# Audio:
audio-library-name p3openal_audio

# Art assets:
model-path ../resources

# Server:
server-version dev
accountdb-type developer
access-level-clamp 600 700

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

# DC file:
dc-file astron/dclass/vanilla.dc

# Core features:
want-kaldron-network #f
want-multiplayer #t
want-pets #f
want-parties #f
want-achievements #f
want-grouptracker #f
want-suit-planners #t

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

# Cashbot boss:
want-resistance-toonup #t
want-resistance-restock #t
want-resistance-dance #t

# Trolley minigames:
want-ttc-trolley #f
want-photo-game #f
want-travel-game #f

# Chat:
want-whitelist #f
want-blacklist #f

# Double progression:
want-double-progression #t

# Developer options:
force-skip-tutorial #t
show-population #f
want-instant-parties #t
want-quest-verification #t
want-heartbeat #f

#notify-level-TownBattle debug
#notify-level-TownBattleToonPanel debug
#notify-level-GagInventoryGui debug
#notify-level-DistributedBattleAI debug
#notify-level-BattleCalculatorAI debug
#notify-level-DistributedBattle debug
#notify-level-ChooseAvatarPanel debug
notify-level-GagInventoryAI debug
notify-level-GagInventory debug
notify-level-GagLoadoutAI debug
notify-level-GagLoadout debug
notify-level-LoadoutSelectGui debug
notify-level-DistributedNPCClerk debug
notify-level-DistributedNPCClerkAI debug

# Debug tools:
want-leak-graph-ai #f
want-leak-graph-client #f

# Safezone interactables:
want-ttc-jukebox #t

# Mod tools:
want-mods #f
