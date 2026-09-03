# Distribution:
distribution host

# Server-only settings for a player hosting their instance of Toontown Infinite.
#
# A hosted server has no website behind it so it can't answer to a gateway.
# The launcher's local profile is the credential instead.
accountdb-type offline

# MongoDB:
mongodb-url mongodb://localhost/game

# UberDOG:
generate-root-object #t

# The host's settings, which the launcher's Hosting screen and `--dedicated`
# both read and write:
host-settings-file server-settings.json

# Where the district reports who is online, for the launcher to poll:
host-status-file server-status.json

# Website services:
want-game-gateway #f

# Audio (live.prc already turns audio on for the client):
audio-library-name null
