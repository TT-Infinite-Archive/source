import enum
from toontown.toonbase import ToontownGlobals

# This is a bboard key for a bool that, if True, indicates that we know
# that the mood of localAvatar's pet has changed in the DB. If true, upon
# opening our pet's avatar panel, we will re-query the game server to get
# updated mood info, and clear this flag from the bboard. Note that the
# flag is only used by code that runs when the pet is not instantiated on
# the client.
# Any system that knows that the mood of localAvatar's pet has changed
# should set this flag in the bboard. Currently this is only the estates
# and pets-in-battle. Note that if the pet is instantiated on the client
# (i.e. in the estate), the flag only needs to be set upon disable/delete
# of the pet.
OurPetsMoodChangedKey = 'OurPetsMoodChanged'

ThinkPeriod = 1.5
MoodDriftPeriod = 300.0
MovePeriod = 0.02
PosBroadcastPeriod = 1.0 / 5.0
LonelinessUpdatePeriod = 60.0

# how far underwater pets float
SubmergeDistance = 0.7

# how many avatars a pet can be aware of
MaxAvatarAwareness = 3

# avatars that are farther than this distance can't be paying attention to us
NonPetSphereRadius = 5.0
# pets that are father than this distance can't be paying attention to us
PetSphereRadius = 3.0

# time over which to examine the number of collisions to detect pet being stuck
UnstickSampleWindow = 20
# number of collisions at which we're considered 'stuck'
UnstickCollisionThreshold = int(0.5 * UnstickSampleWindow)

# Pet Goal Priorities
# some goals will calculate a priority based on these numbers
# others will use them straight
PriorityFleeFromAvatar = 0.6
PriorityDefault = 1.0
PriorityChaseAv = 1.0
PriorityDebugLeash = 50.0
PriorityDoTrick = 100.0

# when a goal becomes the primary goal, its priority is bumped up and
# then slowly decayed to its normal level.
# This is the duration of the deacy.
PrimaryGoalDecayDur = 60.0
# This is the initial increase factor
PrimaryGoalScale = 1.3
HungerChaseToonScale = 1.2
FleeFromOwnerScale = 0.5

GettingAttentionGoalScale = 1.2
# scale does not ramp down; it stays for this long
GettingAttentionGoalScaleDur = 7.0

# these are general, high-level moods that directly correspond to the sets
# of body animations (walk, neutral) that we have for pets
class EAnimMood(enum.IntEnum):
    EXCITED = 0
    SAD = 1
    NEUTRAL = 2

# movement speeds
FwdSpeed = 8.0
RotSpeed = 360.0

_HappyMult = 1.0
HappyFwdSpeed = FwdSpeed * _HappyMult
HappyRotSpeed = RotSpeed * _HappyMult

_SadMult = 0.3
SadFwdSpeed = FwdSpeed * _SadMult
SadRotSpeed = RotSpeed * _SadMult

# Petshop stuff
PETCLERK_TIMER = 180

# Modes for DistributedPet setMovie
PET_MOVIE_CLEAR = 0
PET_MOVIE_START = 1
PET_MOVIE_COMPLETE = 2
PET_MOVIE_FEED = 3
PET_MOVIE_SCRATCH = 4
PET_MOVIE_CALL = 5

FEED_TIME = 10.25
SCRATCH_TIME = 8.15
CALL_TIME = 8.0 / 3

FEED_DIST = {'long': 4.0,
             'medium': 4.0,
             'short': 4.0}

FEED_AMOUNT = 1

SCRATCH_DIST = {'long': 2.0,
                'medium': 1.5,
                'short': 1.0}

TELEPORT_IN_DURATION = 2.34
TELEPORT_OUT_DURATION = 4.5

ZoneToCostRange = {ToontownGlobals.ToontownCentral: (100, 500),
                   ToontownGlobals.DonaldsDock: (600, 1700),
                   ToontownGlobals.DaisyGardens: (1000, 2500),
                   ToontownGlobals.MinniesMelodyland: (1500, 3000),
                   ToontownGlobals.TheBrrrgh: (2500, 4000),
                   ToontownGlobals.DonaldsDreamland: (3000, 5000)}
