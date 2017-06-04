# NOTE: \a is the delimiter for chat pages
# Quest ids can be found in Quests.py
SCRIPT = '''
ID reward_100
SHOW laffMeter
LERP_POS laffMeter 0 0 0 1
LERP_SCALE laffMeter 0.2 0.2 0.2 1
WAIT 1.5
ADD_LAFFMETER 1
WAIT 1
LERP_POS laffMeter -1.18 0 -0.87 1
LERP_SCALE laffMeter 0.075 0.075 0.075 1
WAIT 1
FINISH_QUEST_MOVIE

ID tutorial_mickey
LOCK_LOCALTOON
REPARENTTO camera render
POSHPRSCALE camera 11 7 3 52 0 0 1 1 1
POS localToon 0 0 5
HPR localToon 0 0 0
WAIT 2
LERP_POS localToon -1.8 14.4 0 2
WAIT 1.1
LOOP_ANIM localToon "slip-backward"
WAIT 2.3
#LERP_HPR localToon -110 0 0 0.5
#LERP_HPR localToon -70 0 0 0.55
WAIT 0.4
LOOP_ANIM localToon "neutral"
WAIT 1.0867
# REPARENTTO camera localToon
FREE_LOCALTOON

ID quest_assign_101
CLEAR_CHAT npc
FINISH_QUEST_MOVIE

ID quest_incomplete_110
FINISH_QUEST_MOVIE

ID quest_incomplete_115
REPARENTTO camera npc
WAIT 3
FINISH_QUEST_MOVIE

ID tutorial_blocker
LOAD_DIALOGUE blockerDialogue_01 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker01.mp3"
LOAD_DIALOGUE blockerDialogue_02 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker02.mp3"
LOAD_DIALOGUE blockerDialogue_03 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker03.mp3"
LOAD_DIALOGUE blockerDialogue_04 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker04.mp3"
LOAD_DIALOGUE blockerDialogue_05a "phase_3.5/audio/dial/CC_flippy_tutorial_blocker05.mp3"
LOAD_DIALOGUE blockerDialogue_05b "phase_3.5/audio/dial/CC_flippy_tutorial_blocker06.mp3"
LOAD_DIALOGUE blockerDialogue_06 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker07.mp3"
LOAD_DIALOGUE blockerDialogue_07 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker08.mp3"
LOAD_DIALOGUE blockerDialogue_08 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker09.mp3"
HIDE localToon
REPARENTTO camera npc
FUNCTION npc "stopLookAround"
POS camera 0.0 6.0 4.0
HPR camera 180.0 0.0 0.0
SET_MUSIC_VOLUME 0.4 music 0.5 0.8
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_1 blockerDialogue_01
WAIT 0.8 
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_2 blockerDialogue_02
WAIT 0.8 
POS camera -5.0 -9.0 6.0
HPR camera -25.0 -10.0 0.0
POS localToon 203.8 18.64 -0.475
HPR localToon -90.0 0.0 0.0
SHOW localToon
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_3 blockerDialogue_03
OBSCURE_CHAT 1 0
SHOW chatScButton
WAIT 0.6 
ARROWS_ON -1.3644 0.91 180 -1.5644 0.74 -90 
LOCAL_CHAT_PERSIST npc QuestScriptTutorialBlocker_4 blockerDialogue_04
WAIT_EVENT "enterSpeedChat"
ARROWS_OFF
BLACK_CAT_LISTEN 1
WAIT_EVENT "SCChatEvent"
BLACK_CAT_LISTEN 0
WAIT 0.5
CLEAR_CHAT localToon
REPARENTTO camera localToon
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_5 "CFReversed" blockerDialogue_05a blockerDialogue_05b
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_6 "CFReversed" blockerDialogue_06
OBSCURE_CHAT 0 0 
SHOW chatNormalButton
WAIT 0.6 
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_7 "CFReversed" blockerDialogue_07
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_8 1 "CFReversed" blockerDialogue_08
SET_MUSIC_VOLUME 0.8 music 1.0 0.4
LOOP_ANIM npc "walk"
LERP_HPR npc 270 0 0 0.5
WAIT 0.5
LOOP_ANIM npc "run"
LERP_POS npc 217.4 18.81 -0.475 0.75 
LERP_HPR npc 240 0 0 0.75 
WAIT 0.75
LERP_POS npc 222.4 15.0 -0.475 0.35
LERP_HPR npc 180 0 0 0.35
WAIT 0.35
LERP_POS npc 222.4 5.0 -0.475 0.75
WAIT 0.75
REPARENTTO npc hidden
FREE_LOCALTOON
UPON_TIMEOUT ARROWS_OFF
UPON_TIMEOUT OBSCURE_CHAT 0 0 
UPON_TIMEOUT REPARENTTO camera localToon
FINISH_QUEST_MOVIE

ID gag_intro
SEND_EVENT "disableGagPanel"
SEND_EVENT "disableBackToPlayground"
HIDE inventory
TOON_HEAD npc 0 0 1
WAIT 0.1
# Welcome to the Gag Shop!
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_1
LERP_POS npcToonHead -0.64 0 -0.74 0.7
LERP_SCALE npcToonHead 0.82 0.82 0.82 0.7
LERP_COLOR_SCALE purchaseBg 1 1 1 1  0.6 0.6 0.6 1 0.7
WAIT 0.7
SHOW inventory
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_1a
## here's your jb jar
#ARROWS_ON -1.22 0.09 0 -0.93 -0.2 -90 
#LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_2
#ARROWS_OFF
# try buying a gag
ARROWS_ON -0.19 0.04 180 -0.4 0.26 90
LOCAL_CHAT_PERSIST npc QuestScriptGagShop_3
SEND_EVENT "enableGagPanel"
WAIT_EVENT "inventory-selection"
ARROWS_OFF
CLEAR_CHAT npc
WAIT 0.5
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_4
# show advanced throw & squirt gags
LOCAL_CHAT_PERSIST npc QuestScriptGagShop_5
WAIT 0.5
SHOW_THROW_SQUIRT_PREVIEW
CLEAR_CHAT npc
WAIT 0.5
# show "Exit Back To Playground" button
SET_BIN backToPlaygroundButton "gui-popup"
LERP_POS backToPlaygroundButton -0.12 0 0.18 0.5
LERP_SCALE backToPlaygroundButton 2 2 2 0.5
LERP_COLOR_SCALE backToPlaygroundButton 1 1 1 1  2.78 2.78 2.78 1 0.5
LERP_COLOR_SCALE inventory 1 1 1 1  0.6 0.6 0.6 1 0.5
WAIT 0.5
START_THROB backToPlaygroundButton 2.78 2.78 2.78 1  2.78 2.78 2.78 0.7  2
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_6
STOP_THROB
LERP_POS backToPlaygroundButton 0.72 0 -0.045 0.5
LERP_SCALE backToPlaygroundButton 1.04 1.04 1.04 0.5
LERP_COLOR_SCALE backToPlaygroundButton 2.78 2.78 2.78 1  1 1 1 1 0.5
WAIT 0.5
CLEAR_BIN backToPlaygroundButton
# show "Play Again" button
SET_BIN playAgainButton "gui-popup"
LERP_POS playAgainButton -0.12 0 0.18 0.5
LERP_SCALE playAgainButton 2 2 2 0.5
LERP_COLOR_SCALE playAgainButton 1 1 1 1  2.78 2.78 2.78 1 0.5
WAIT 0.5
START_THROB playAgainButton 2.78 2.78 2.78 1  2.78 2.78 2.78 0.7  2
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_7
STOP_THROB
LERP_POS playAgainButton 0.72 0 -0.24 0.5
LERP_SCALE playAgainButton 1.04 1.04 1.04 0.5
LERP_COLOR_SCALE playAgainButton 2.78 2.78 2.78 1  1 1 1 1 0.5
WAIT 0.5
CLEAR_BIN playAgainButton
# You're needed in Toon HQ!
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_8 1
TOON_HEAD npc 0 0 0
LERP_COLOR_SCALE inventory 0.6 0.6 0.6 1  1 1 1 1 0.5
LERP_COLOR_SCALE purchaseBg 0.6 0.6 0.6 1  1 1 1 1 0.5
WAIT 0.5
SEND_EVENT "enableBackToPlayground"
UPON_TIMEOUT TOON_HEAD npc 0 0 0
UPON_TIMEOUT ARROWS_OFF
UPON_TIMEOUT SHOW inventory
UPON_TIMEOUT SEND_EVENT "enableGagPanel"
UPON_TIMEOUT SEND_EVENT "enableBackToPlayground"
ID quest_incomplete_120
CHAT_CONFIRM npc QuestScript120_1
# ANIM
CHAT_CONFIRM npc QuestScript120_2 1
FINISH_QUEST_MOVIE
ID quest_assign_121
CHAT_CONFIRM npc QuestScript121_1 1
FINISH_QUEST_MOVIE
ID quest_assign_130
CHAT_CONFIRM npc QuestScript130_1 1
FINISH_QUEST_MOVIE
ID quest_assign_131
CHAT_CONFIRM npc QuestScript131_1 1
FINISH_QUEST_MOVIE
ID quest_assign_140
CHAT_CONFIRM npc QuestScript140_1 1
FINISH_QUEST_MOVIE
ID quest_assign_141
CHAT_CONFIRM npc QuestScript141_1 1
FINISH_QUEST_MOVIE
ID quest_incomplete_145
CHAT_CONFIRM npc QuestScript145_1 1
LOAD frame "phase_4/models/gui/tfa_images" "FrameBlankA"
LOAD tunnel "phase_4/models/gui/tfa_images" "tunnelSignA"
POSHPRSCALE tunnel 0 0 0 0 0 0 0.8 0.8 0.8
REPARENTTO tunnel frame
POSHPRSCALE frame 0 0 0 0 0 0 0.1 0.1 0.1
REPARENTTO frame aspect2d
LERP_SCALE frame 1.0 1.0 1.0 1.0
WAIT 3.0
LERP_SCALE frame 0.1 0.1 0.1 0.5
WAIT 0.5
REPARENTTO frame hidden
CHAT_CONFIRM npc QuestScript145_2 1
UPON_TIMEOUT FUNCTION frame "removeNode"
FINISH_QUEST_MOVIE
ID quest_incomplete_150
CHAT_CONFIRM npc QuestScript150_1
ARROWS_ON  1.65 0.51 -120 1.65 0.51 -120
SHOW_FRIENDS_LIST
CHAT_CONFIRM npc QuestScript150_2
ARROWS_OFF
HIDE_FRIENDS_LIST
CHAT_CONFIRM npc QuestScript150_3
HIDE bFriendsList
CHAT_CONFIRM npc QuestScript150_4 1
UPON_TIMEOUT HIDE_FRIENDS_LIST
UPON_TIMEOUT ARROWS_OFF
FINISH_QUEST_MOVIE
'''