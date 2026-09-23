# Client-only configuration, shared by every distribution. No server loads it,
# so nothing the AI or UberDOG reads belongs here.

# Window settings:
window-title Toontown Infinite
win-origin -2 -2
icon-filename phase_3/etc/icon.ico
cursor-filename phase_3/etc/toonmono.cur

# Audio:
audio-library-name p3openal_audio

# Graphics:
# aux-display pandagl
load-display pandagl
aux-display p3tinydisplay

# Preferences:
preferences-path preferences.json

# Content packs:
content-packs-path contentpacks

# Performance:
sync-video #f
gl-check-errors #f

# Intel:
stencil-bits 1
depth-bits 24
allow-incomplete-render #f
