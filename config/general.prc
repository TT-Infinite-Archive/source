# Window settings:
window-title Toontown Infinite
win-origin -1 -1
icon-filename phase_3/etc/icon.ico
cursor-filename phase_3/etc/toonmono.cur

# Audio:
audio-library-name null

# Graphics:
# aux-display pandagl
load-display pandagl
aux-display p3tinydisplay
text-pixels-per-unit 128

# Models:
model-cache-models #f
model-cache-textures #f
default-model-extension .bam

# Textures:
texture-anisotropic-degree 16

# Preferences:
preferences-path preferences.json

# Content packs:
content-packs-path contentpacks

# Backups:
backups-filepath backups/
backups-extension .json

# Server:
server-timezone PST/PDT/-8
server-port 7000
account-server-endpoint https://toontowninfinite.com/api/

# RPC:
want-rpc-server #f
rpc-server-endpoint http://localhost:8080/
rpc-server-secret eWd54mrNYuREmTA6

# Website gateway:
want-game-gateway #t
shard-heartbeat-interval 20

# Performance:
sync-video #f
texture-power-2 none
gl-check-errors #f
garbage-collect-states #t
support-threads #t
loader-num-threads 35

# Egg object types:
egg-object-type-barrier <Scalar> collide-mask { 0x01 } <Collide> { Polyset descend }
egg-object-type-trigger <Scalar> collide-mask { 0x01 } <Collide> { Polyset descend intangible }
egg-object-type-sphere <Scalar> collide-mask { 0x01 } <Collide> { Sphere descend }
egg-object-type-trigger-sphere <Scalar> collide-mask { 0x01 } <Collide> { Sphere descend intangible }
egg-object-type-floor <Scalar> collide-mask { 0x02 } <Collide> { Polyset descend }
egg-object-type-dupefloor <Scalar> collide-mask { 0x02 } <Collide> { Polyset keep descend }
egg-object-type-camera-collide <Scalar> collide-mask { 0x04 } <Collide> { Polyset descend }
egg-object-type-camera-collide-sphere <Scalar> collide-mask { 0x04 } <Collide> { Sphere descend }
egg-object-type-camera-barrier <Scalar> collide-mask { 0x05 } <Collide> { Polyset descend }
egg-object-type-camera-barrier-sphere <Scalar> collide-mask { 0x05 } <Collide> { Sphere descend }
egg-object-type-model <Model> { 1 }
egg-object-type-dcs <DCS> { 1 }

# Core features:
want-kaldron-network #f
want-multiplayer #f
want-guilds #f
want-guild-quests #f
want-emblems #f
want-gardening #t
want-pets #t

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

# Safe zone settings:
want-treasure-planners #t
want-suit-planners #t

# Classic characters:
want-classic-chars #f
want-mickey #f
want-donald-dock #f
want-daisy #f
want-minnie #f
want-pluto #f
want-donald-dreamland #f
want-chip-and-dale #f
want-goofy #f

# Trolley minigames:
want-minigames #t
want-photo-game #f
want-travel-game #f
want-ttc-trolley #t

# Picnic table board games:
want-game-tables #f

# Cog headquarters:
want-cog-headquarters #t
want-sellbot-headquarters #t
want-cashbot-headquarters #t
want-lawbot-headquarters #t
want-bossbot-headquarters #t

# Cashbot boss:
want-resistance-toonup #t
want-resistance-restock #t
want-resistance-dance #f

# Cog battles:
base-xp-multiplier 1.0

# Animated Props
zero-pause-mult 1.0

# Interactive Props
randomize-interactive-idles #t
interactive-prop-random-idles #t
interactive-prop-info #f
props-buff-battles #t
prop-and-organic-bonus-stack #f
prop-idle-pause-time 0.0

# Optional:
show-total-population #t
want-mat-all-tailors #t
want-long-pattern-game #f
want-talkative-tyler #f
want-yin-yang #f
want-butterflies #f
want-estate-fisherman #t
want-fireworks #t
want-code-redemption #f

# Developer options:
want-dev #f
want-pstats 0
want-threaded-ai-start #f

# Temporary:
smooth-lag 0.4
want-old-fireworks #t

# Live updates:
want-live-updates #t

# Heartbeat
want-heartbeat #t

# Toon patches:
toon-patch-version 0

# Intel:
stencil-bits 1
depth-bits 24
allow-incomplete-render #f