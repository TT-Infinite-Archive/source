# Distribution:
distribution host

# Server-only settings for a player hosting their own server from the game.
#
# A hosted server has no website behind it so it can't answer to a gateway.
# The launcher's local profile is the credential instead.
accountdb-type offline

# MongoDB:
mongodb-url mongodb://localhost/game

# UberDOG:
generate-root-object #t

# Website services:
want-game-gateway #f

# Audio (live.prc already turns audio on for the client):
audio-library-name null
