import random

GUILD_QUEST_EMPTY = [0, 0, 0, 0]

# Field Indexes
GUILD_QUEST_ID = 0
GUILD_QUEST_GOAL = 1
GUILD_QUEST_REWARD = 2
GUILD_QUEST_PROGRESS = 3


def getQuestFromNum(questNum, repeat=0):
    # Seed with the date so that everyone gets the same quest
    seed = questNum
    random.seed(seed)
    # Pick a random category
    category = random.choice(GUILD_QUEST_CATEGORIES)
    # Pick a random objective for that category
    random.seed(seed)
    questId = random.choice(GUILD_QUEST_CAT_TO_IDS[category])
    # Get the whole quest structure
    quest = GuildQuestDict[questId]
    # Get other information from quest
    rewardPer = quest[2]
    possibleAmounts = quest[3]
    # Pick a random amount of objective to 'do'
    random.seed(seed)
    goal = random.choice(possibleAmounts)
    # Generate the reward for this quest
    reward = goal * rewardPer

    # Our quest task has been generated
    task = [
        questId,
        goal,
        reward,
        0
    ]
    if not repeat and (getQuestFromNum(seed-1, 1) == task):
        # This ques repeats, lets give them the default quest
        random.seed(seed)
        questId = random.choice(GUILD_QUEST_CAT_TO_IDS[GUILD_QUEST_CAT_REPEAT])
        quest = GuildQuestDict[questId]
        rewardPer = quest[2]
        possibleAmounts = quest[3]
        random.seed(seed)
        goal = random.choice(possibleAmounts)
        reward = goal * rewardPer
        task = [
            questId,
            goal,
            reward,
            0
        ]

    return task

# All possible guild quest categories
GUILD_QUEST_CAT_COG = 0             # Defeat cogs
GUILD_QUEST_CAT_INSTANCE = 1        # Defeat instances
GUILD_QUEST_CAT_BOSS = 2            # Defeat a boss
GUILD_QUEST_CAT_FISH = 3            # Catch fish
GUILD_QUEST_CAT_TROLLEY = 4         # Play trolley
GUILD_QUEST_CAT_GOLF = 5            # Play golf
GUILD_QUEST_CAT_REPEAT = 6          # If the guild repeats, give them one of these

GUILD_QUEST_CATEGORIES = [
    GUILD_QUEST_CAT_COG,
    GUILD_QUEST_CAT_INSTANCE,
    GUILD_QUEST_CAT_BOSS,
    GUILD_QUEST_CAT_FISH,
    GUILD_QUEST_CAT_TROLLEY,
    GUILD_QUEST_CAT_GOLF
]

GUILD_QUEST_CAT_TO_IDS = {
    GUILD_QUEST_CAT_COG: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                          26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36),
    GUILD_QUEST_CAT_INSTANCE: (37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51),
    GUILD_QUEST_CAT_BOSS: (52, 53, 54, 55, 56),
    GUILD_QUEST_CAT_FISH: (57, 58, 59, 60, 61, 62, 63, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79,
                           80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97, 98, 99, 100, 101,
                           102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 115, 116, 117,
                           120, 121, 122, 123, 124, 125),
    GUILD_QUEST_CAT_TROLLEY: (128,),
    GUILD_QUEST_CAT_GOLF: (130, 131, 132, 133),
    GUILD_QUEST_CAT_REPEAT: (129, 130, 128, 52)
}


# Quest Dict Structure: id: [category, objective string, rewardPer, (possible goals)]
GuildQuestDict = {
    0: [GUILD_QUEST_CAT_COG, 'any', 1, (50, 250, 500, 750, 1000, 1250)],
    1: [GUILD_QUEST_CAT_COG, 'sellbot', 1, (100, 300, 600, 900, 1200)],
    2: [GUILD_QUEST_CAT_COG, 'cashbot', 1, (100, 300, 600, 900, 1200)],
    3: [GUILD_QUEST_CAT_COG, 'lawbot', 1, (100, 300, 600, 900, 1200)],
    4: [GUILD_QUEST_CAT_COG, 'bossbot', 1, (100, 300, 600, 900, 1200)],
    5: [GUILD_QUEST_CAT_COG, 'f', 2, (75, 100, 125, 150)],
    6: [GUILD_QUEST_CAT_COG, 'p', 2, (75, 100, 125, 150)],
    7: [GUILD_QUEST_CAT_COG, 'ym', 2, (75, 100, 125, 150)],
    8: [GUILD_QUEST_CAT_COG, 'mm', 2, (75, 100, 125, 150)],
    9: [GUILD_QUEST_CAT_COG, 'ds', 2, (75, 100, 125, 150)],
    10: [GUILD_QUEST_CAT_COG, 'hh', 2, (75, 100, 125, 150)],
    11: [GUILD_QUEST_CAT_COG, 'cr', 2, (75, 100, 125, 150)],
    12: [GUILD_QUEST_CAT_COG, 'tbc', 2, (75, 100, 125, 150)],
    13: [GUILD_QUEST_CAT_COG, 'bf', 2, (75, 100, 125, 150)],
    14: [GUILD_QUEST_CAT_COG, 'b', 2, (75, 100, 125, 150)],
    15: [GUILD_QUEST_CAT_COG, 'dt', 2, (75, 100, 125, 150)],
    16: [GUILD_QUEST_CAT_COG, 'ac', 2, (75, 100, 125, 150)],
    17: [GUILD_QUEST_CAT_COG, 'bs', 2, (75, 100, 125, 150)],
    18: [GUILD_QUEST_CAT_COG, 'sd', 2, (75, 100, 125, 150)],
    19: [GUILD_QUEST_CAT_COG, 'le', 2, (75, 100, 125, 150)],
    20: [GUILD_QUEST_CAT_COG, 'bw', 2, (75, 100, 125, 150)],
    21: [GUILD_QUEST_CAT_COG, 'sc', 2, (75, 100, 125, 150)],
    22: [GUILD_QUEST_CAT_COG, 'pp', 2, (75, 100, 125, 150)],
    23: [GUILD_QUEST_CAT_COG, 'tw', 2, (75, 100, 125, 150)],
    24: [GUILD_QUEST_CAT_COG, 'bc', 2, (75, 100, 125, 150)],
    25: [GUILD_QUEST_CAT_COG, 'nc', 2, (75, 100, 125, 150)],
    26: [GUILD_QUEST_CAT_COG, 'mb', 2, (75, 100, 125, 150)],
    27: [GUILD_QUEST_CAT_COG, 'ls', 2, (75, 100, 125, 150)],
    28: [GUILD_QUEST_CAT_COG, 'rb', 2, (75, 100, 125, 150)],
    29: [GUILD_QUEST_CAT_COG, 'cc', 2, (75, 100, 125, 150)],
    30: [GUILD_QUEST_CAT_COG, 'tm', 2, (75, 100, 125, 150)],
    31: [GUILD_QUEST_CAT_COG, 'nd', 2, (75, 100, 125, 150)],
    32: [GUILD_QUEST_CAT_COG, 'gh', 2, (75, 100, 125, 150)],
    33: [GUILD_QUEST_CAT_COG, 'ms', 2, (75, 100, 125, 150)],
    34: [GUILD_QUEST_CAT_COG, 'tf', 2, (75, 100, 125, 150)],
    35: [GUILD_QUEST_CAT_COG, 'm', 2, (75, 100, 125, 150)],
    36: [GUILD_QUEST_CAT_COG, 'mh', 2, (75, 100, 125, 150)],
    37: [GUILD_QUEST_CAT_INSTANCE, 'sellbot', 10, (5, 7, 10)],
    38: [GUILD_QUEST_CAT_INSTANCE, 'cashbot', 15, (5, 7, 10)],
    39: [GUILD_QUEST_CAT_INSTANCE, 'lawbot', 15, (5, 7, 10)],
    40: [GUILD_QUEST_CAT_INSTANCE, 'bossbot', 15, (5, 7, 10)],
    41: [GUILD_QUEST_CAT_INSTANCE, 'factory', 15, (5, 7, 10)],
    42: [GUILD_QUEST_CAT_INSTANCE, 'coin-mint', 15, (5, 7, 10)],
    43: [GUILD_QUEST_CAT_INSTANCE, 'dollar-mint', 15, (5, 7,)],
    44: [GUILD_QUEST_CAT_INSTANCE, 'bullion-mint', 15, (5, 7,)],
    45: [GUILD_QUEST_CAT_INSTANCE, 'office-a', 15, (5, 7, 10)],
    46: [GUILD_QUEST_CAT_INSTANCE, 'office-b', 20, (5, 7, 10)],
    47: [GUILD_QUEST_CAT_INSTANCE, 'office-c', 20, (5, 7)],
    48: [GUILD_QUEST_CAT_INSTANCE, 'office-d', 25, (5, 7)],
    49: [GUILD_QUEST_CAT_INSTANCE, 'front-three', 15, (5, 7,)],
    50: [GUILD_QUEST_CAT_INSTANCE, 'middle-six', 20, (3,)],
    51: [GUILD_QUEST_CAT_INSTANCE, 'back-nine', 20, (3,)],
    52: [GUILD_QUEST_CAT_BOSS, 'any', 50, (1, 3, 5)],
    53: [GUILD_QUEST_CAT_BOSS, 'sellbot', 50, (1, 3, 5)],
    54: [GUILD_QUEST_CAT_BOSS, 'cashbot', 75, (1, 3, 5)],
    55: [GUILD_QUEST_CAT_BOSS, 'lawbot', 100, (1, 3, 5)],
    56: [GUILD_QUEST_CAT_BOSS, 'bossbot', 125, (1, 3, 5)],
    57: [GUILD_QUEST_CAT_FISH, 'any', 1, (50, 75, 100)],
    58: [GUILD_QUEST_CAT_FISH, 'Balloon Fish', 5, (20, 35, 50)],
    59: [GUILD_QUEST_CAT_FISH, 'Hot Air Balloon Fish', 5, (20, 35, 50)],
    60: [GUILD_QUEST_CAT_FISH, 'Weather Balloon Fish', 5, (20, 35, 50)],
    61: [GUILD_QUEST_CAT_FISH, 'Water Balloon Fish', 5, (20, 35, 50)],
    62: [GUILD_QUEST_CAT_FISH, 'Red Balloon Fish', 5, (20, 35, 50)],
    63: [GUILD_QUEST_CAT_FISH, 'Cat Fish', 5, (20, 35, 50)],
    65: [GUILD_QUEST_CAT_FISH, 'Alley Cat Fish', 5, (20, 35, 50)],
    66: [GUILD_QUEST_CAT_FISH, 'Tabby Cat Fish', 5, (20, 35, 50)],
    67: [GUILD_QUEST_CAT_FISH, 'Tom Cat Fish', 5, (20, 35, 50)],
    68: [GUILD_QUEST_CAT_FISH, 'Clown Fish', 5, (20, 35, 50)],
    69: [GUILD_QUEST_CAT_FISH, 'Sad Clown Fish', 5, (20, 35, 50)],
    70: [GUILD_QUEST_CAT_FISH, 'Party Clown Fish', 5, (20, 35, 50)],
    71: [GUILD_QUEST_CAT_FISH, 'Circus Clown Fish', 50, (3, 5)],
    72: [GUILD_QUEST_CAT_FISH, 'Frozen Fish', 5, (20, 35, 50)],
    73: [GUILD_QUEST_CAT_FISH, 'Star Fish', 5, (20, 35, 50)],
    74: [GUILD_QUEST_CAT_FISH, 'Five Star Fish', 5, (20, 35, 50)],
    75: [GUILD_QUEST_CAT_FISH, 'Rock Star Fish', 5, (20, 35, 50)],
    76: [GUILD_QUEST_CAT_FISH, 'Shining Star Fish', 5, (20, 35, 50)],
    79: [GUILD_QUEST_CAT_FISH, 'Dog Fish', 5, (20, 35, 50)],
    80: [GUILD_QUEST_CAT_FISH, 'Bull Dog Fish', 50, (3, 5)],
    81: [GUILD_QUEST_CAT_FISH, 'Hot Dog Fish', 5, (20, 35, 50)],
    82: [GUILD_QUEST_CAT_FISH, 'Puppy Dog Fish', 5, (20, 35, 50)],
    83: [GUILD_QUEST_CAT_FISH, 'Dalmatian Dog Fish', 5, (20, 35, 50)],
    84: [GUILD_QUEST_CAT_FISH, 'Amore Eel', 5, (20, 35, 50)],
    85: [GUILD_QUEST_CAT_FISH, 'Electric Amore Eel', 5, (20, 35, 50)],
    86: [GUILD_QUEST_CAT_FISH, 'Nurse Shark', 5, (20, 35, 50)],
    87: [GUILD_QUEST_CAT_FISH, 'Clara Nurse Shark', 50, (3, 5)],
    88: [GUILD_QUEST_CAT_FISH, 'Florence Nurse Shark', 50, (3, 5)],
    89: [GUILD_QUEST_CAT_FISH, 'King Crab', 5, (20, 35, 50)],
    90: [GUILD_QUEST_CAT_FISH, 'Alaskan King Crab', 50, (3, 5)],
    91: [GUILD_QUEST_CAT_FISH, 'Old King Crab', 50, (3, 5)],
    92: [GUILD_QUEST_CAT_FISH, 'Moon Fish', 5, (20, 35, 50)],
    94: [GUILD_QUEST_CAT_FISH, 'Half Moon Fish', 50, (3, 5)],
    95: [GUILD_QUEST_CAT_FISH, 'New Moon Fish', 5, (20, 35, 50)],
    96: [GUILD_QUEST_CAT_FISH, 'Crescent Moon Fish', 50, (3, 5)],
    97: [GUILD_QUEST_CAT_FISH, 'Harvest Moon Fish', 5, (20, 35, 50)],
    98: [GUILD_QUEST_CAT_FISH, 'Sea Horse', 5, (20, 35, 50)],
    99: [GUILD_QUEST_CAT_FISH, 'Rocking Sea Horse', 5, (20, 35, 50)],
    100: [GUILD_QUEST_CAT_FISH, 'Clydesdale Sea Horse', 5, (20, 35, 50)],
    101: [GUILD_QUEST_CAT_FISH, 'Arabian Sea Horse', 50, (3, 5)],
    102: [GUILD_QUEST_CAT_FISH, 'Pool Shark', 5, (20, 35, 50)],
    103: [GUILD_QUEST_CAT_FISH, 'Kiddie Pool Shark', 5, (20, 35, 50)],
    104: [GUILD_QUEST_CAT_FISH, 'Swimming Pool Shark', 5, (20, 35, 50)],
    105: [GUILD_QUEST_CAT_FISH, 'Olympic Pool Shark', 50, (3, 5)],
    106: [GUILD_QUEST_CAT_FISH, 'Brown Bear Acuda', 5, (20, 35, 50)],
    107: [GUILD_QUEST_CAT_FISH, 'Black Bear Acuda', 5, (20, 35, 50)],
    108: [GUILD_QUEST_CAT_FISH, 'Koala Bear Acuda', 5, (20, 35, 50)],
    109: [GUILD_QUEST_CAT_FISH, 'Honey Bear Acuda', 5, (20, 35, 50)],
    110: [GUILD_QUEST_CAT_FISH, 'Polar Bear Acuda', 50, (3, 5)],
    111: [GUILD_QUEST_CAT_FISH, 'Panda Bear Acuda', 50, (3, 5)],
    112: [GUILD_QUEST_CAT_FISH, 'Kodiac Bear Acuda', 50, (3, 5)],
    114: [GUILD_QUEST_CAT_FISH, 'Cutthroat Trout', 5, (20, 35, 50)],
    115: [GUILD_QUEST_CAT_FISH, 'Captain Cutthroat Trout', 50, (3, 5)],
    116: [GUILD_QUEST_CAT_FISH, 'Scurvy Cutthroat Trout', 50, (3, 5)],
    117: [GUILD_QUEST_CAT_FISH, 'Piano Tuna', 5, (20, 35, 50)],
    120: [GUILD_QUEST_CAT_FISH, 'Upright Piano Tuna', 50, (3, 5)],
    121: [GUILD_QUEST_CAT_FISH, 'Player Piano Tuna', 50, (3, 5)],
    122: [GUILD_QUEST_CAT_FISH, 'Peanut Butter & Jellyfish', 5, (20, 35, 50)],
    123: [GUILD_QUEST_CAT_FISH, 'Grape PB&J Fish', 5, (20, 35, 50)],
    124: [GUILD_QUEST_CAT_FISH, 'Crunchy PB&J Fish', 5, (20, 35, 50)],
    125: [GUILD_QUEST_CAT_FISH, 'Strawberry PB&J Fish', 5, (20, 35, 50)],
    128: [GUILD_QUEST_CAT_TROLLEY, 'any', 5, (15, 25, 35, 45, 55)],
    129: [GUILD_QUEST_CAT_COG, 'any', 1, (1500,)],
    130: [GUILD_QUEST_CAT_GOLF, 'any', 20, (5, 7, 10)],
    131: [GUILD_QUEST_CAT_GOLF, 'easy', 15, (5, 7, 10)],
    132: [GUILD_QUEST_CAT_GOLF, 'medium', 25, (3, 5,)],
    133: [GUILD_QUEST_CAT_GOLF, 'hard', 40, (3,)]
}