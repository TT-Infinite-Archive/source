# Distribution:
distribution qa

# Server:
server-version SERVER_VERSION
shard-low-pop 25
shard-mid-pop 50
access-level-clamp 600 700

# Events:
want-storm-event #t

# Core features:
want-pets #t
want-parties #f
want-achievements #f
want-grouptracker #t
want-game-tables #t

# Chat:
want-whitelist #f

# Cashbot boss:
want-resistance-toonup #t
want-resistance-restock #t
want-resistance-dance #t

# Developer options:
show-population #t
force-skip-tutorial #t
want-instant-parties #t

# Notify
notify-level-GuildManager debug
notify-level-GuildManagerUD debug
notify-level-GuildManagerAI debug
notify-level-DistributedNPCLowdenClear debug
notify-level-DistributedNPCLowdenClearAI debug
notify-level-DistributedBossbotBoss debug
notify-level-DistributedBanquetTable debug

# Debug tools:
want-leak-graph #f
