NORMAL_CHAT = 1
WHISPER_CHAT = 2
GUILD_CHAT = 3
CREW_CHAT = 4
SHIPPVP_CHAT = 5
ERROR_NONE = None
ERROR_NO_OPEN_CHAT = 1
ERROR_NOT_FRIENDS = 2
ERROR_NO_RECEIVER = 3
ERROR_NO_GUILD_CHAT = 4
ERROR_NO_CREW_CHAT = 5
ERROR_NO_SHIPPVP_CHAT = 6
TYPEDCHAT = 0
SPEEDCHAT_NORMAL = 1
SPEEDCHAT_EMOTE = 2
SPEEDCHAT_CUSTOM = 3
SYSTEMCHAT = 4
GAMECHAT = 5
GUILDCHAT = 6
PARTYCHAT = 7
SPEEDCHAT_QUEST = 8
FRIEND_UPDATE = 9
CREW_UPDATE = 10
GUILD_UPDATE = 11
AVATAR_UNAVAILABLE = 12
SHIPPVPCHAT = 13
GMCHAT = 14
ChatEvent = 'ChatEvent'
NormalChatEvent = 'NormalChatEvent'
SCChatEvent = 'SCChatEvent'
SCCustomChatEvent = 'SCCustomChatEvent'
SCEmoteChatEvent = 'SCEmoteChatEvent'
SCQuestEvent = 'SCQuestEvent'
OnScreen = 0
OffScreen = 1
Thought = 2
ThoughtPrefix = '.'
ModifierPrefix = '/'
AllModifier = 'all'
GuildModifier = 'guild'
Modifiers = [AllModifier, GuildModifier]
ChannelToType = {
    0: 0,  # All Channel is type 0 (Open)
    1: 2   # Guild Channel is type 2
}

def isThought(message):
    if not message:
        return 0
    if len(message) == 0:
        return 0
    elif message.find(ThoughtPrefix, 0, len(ThoughtPrefix)) >= 0:
        return 1
    else:
        return 0


def isModifier(message):
    if not message:
        return 0
    elif len(message) == 0:
        return 0
    elif message.find(ModifierPrefix, 0, len(ModifierPrefix)) >= 0:
        return 1
    else:
        return 0


def getModifierType(message):
    if not message:
        return None
    if len(message) == 0:
        return None
    for modifier in Modifiers:
        if len(modifier) + 1 > len(message):
            continue
        if message[1:len(modifier) + 1] == modifier:
            return modifier
    return None


def removeModifier(message):
    # Get which modifier to remove
    modifier = getModifierType(message)
    if modifier is None:
        return message

    # Remove the modifier and the modifier prefix
    message = message[len(ModifierPrefix) + len(modifier):]

    return message


def removeThoughtPrefix(message):
    if isThought(message):
        return message[len(ThoughtPrefix):]
    else:
        return message
