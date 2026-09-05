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

# Performance:
sync-video #f
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
want-multiplayer #f
want-guilds #f
want-guild-quests #f
want-emblems #f
want-pets #t

# Safe zones:
want-safe-zones #t
want-minnies-melodyland #t
want-the-burrrgh #t
want-donalds-dreamland #t
want-goofy-speedway #t
want-outdoor-zone #t
want-golf-zone #t

# Trolley minigames:
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
props-buff-battles #t
prop-and-organic-bonus-stack #f
prop-idle-pause-time 0.0

# Optional:
show-total-population #t
want-mat-all-tailors #t
want-long-pattern-game #f
want-talkative-tyler #f
want-yin-yang #f
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

# Connect while the intro cinematic plays
want-connection-warmup #t

# Toon patches:
toon-patch-version 0

# Intel:
stencil-bits 1
depth-bits 24
allow-incomplete-render #f