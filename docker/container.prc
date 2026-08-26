# Art location for the containerised stack, loaded last:
model-path /resources

# Where the rest of the stack is on the compose network:
air-connect astrond:7010
eventlog-host astrond:7020
mongodb-url mongodb://mongo:27017/game
