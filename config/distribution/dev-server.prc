# Distribution:
distribution dev

# Server-only settings for development.

# developer   login screen, any username, accessLevel 500
# offline     login screen, any username, accessLevel 100
# production  no login screen; uses the launcher's launch token
accountdb-type developer

# MongoDB:
mongodb-url mongodb://localhost/game

# UberDOG:
generate-root-object #t

# Live account & gateway services:
want-game-gateway #f
account-service-url http://localhost:4321
gateway-url ws://localhost:4322/api/game/socket
