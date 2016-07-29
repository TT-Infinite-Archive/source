from toontown.toonbase import TTLocalizer

GUILD_MOVIE_START = 0           # Guild creation prompt
GUILD_MOVIE_PROMPT_NAME = 1     # Guild creation name prompt
GUILD_MOVIE_PROMPT_ICON = 2     # Guild creation icon prompt
GUILD_MOVIE_RENAME = 3          # Guild creation rename prompt
GUILD_MOVIE_RENAME_NAME = 4     # Guild creation rename prompt name
GUILD_MOVIE_DONE = 5            # Guild creation icon selected / rename entered
GUILD_MOVIE_DENY = 6            # Guild creation cancelled
GUILD_MOVIE_CLEAR = 7           # Clear npc chat
GUILD_MOVIE_TIMEOUT = 8         # Player took too long to reply
GUILD_MOVIE_REJECT = 9          # Reject player request to interact
GUILD_MOVIE_CONVERSE = 10        # Simply speech, no prompts
GUILD_MOVIE_REJECT_NO_BEANS = 11    # Poor people cant afford guilds!

GUILD_MOVIE_TO_DIALOG = {
    GUILD_MOVIE_START: TTLocalizer.GuildDialogMovieStart,
    GUILD_MOVIE_PROMPT_NAME: TTLocalizer.GuildDialogMoviePromptName,
    GUILD_MOVIE_PROMPT_ICON: TTLocalizer.GuildDialogMoviePromptIcon,
    GUILD_MOVIE_RENAME: TTLocalizer.GuildDialogMovieRename,
    GUILD_MOVIE_RENAME_NAME: TTLocalizer.GuildDialogMovieRenameName,
    GUILD_MOVIE_DONE: TTLocalizer.GuildDialogMovieDone,
    GUILD_MOVIE_DENY: TTLocalizer.GuildDialogMovieDeny,
    GUILD_MOVIE_REJECT_NO_BEANS: TTLocalizer.GuildDialogMovieRejectNoBeans
}

GUILD_COST = 10000