from otp.otpbase.OTPLocalizerServer import *
from panda3d.core import TextProperties, TextPropertiesManager
import string
from otp.otpbase.OTPLocalizerEnglishProperty import *
DialogOK = lOK
DialogCancel = lCancel
DialogYes = lYes
DialogNo = lNo
lClose = 'Close'
lNext = 'Next'
lQuit = 'Quit'
DialogDoNotShowAgain = 'Do Not\nShow Again'
WhisperNoLongerFriend = '%s left your friends list.'
WhisperNowSpecialFriend = '%s is now your True Friend!'
WhisperComingToVisit = '%s is coming to visit you.'
WhisperFailedVisit = '%s tried to visit you.'
WhisperTargetLeftVisit = '%s has gone somewhere else. Try again!'
WhisperGiveupVisit = "%s couldn't find you because you're moving around!"
TeleportGreeting = 'Hi, %s.'
WhisperFriendComingOnline = '%s is coming online!'
WhisperFriendLoggedOut = '%s has logged out.'
WhisperPlayerOnline = '%s logged into %s'
WhisperPlayerOffline = '%s is offline.'
WhisperUnavailable = 'That player is no longer available for whispers.'
DialogSpecial = 'ooo'
DialogExclamation = '!'
DialogQuestion = '?'
ChatInputNormalSayIt = 'Say It'
ChatInputNormalCancel = lCancel
ChatInputNormalWhisper = 'Whisper'
ChatInputWhisperLabel = 'To %s'
SCEmoteNoAccessMsg = 'You do not have access\nto this emotion yet.'
SCEmoteNoAccessOK = lOK
ParentLogin = 'Parent Login'
ParentPassword = 'Parent Account Password'
ChatGarblerDefault = ['blah']
ChatManagerChat = 'Chat'
ChatManagerWhisperTo = 'Whisper to:'
ChatManagerWhisperToName = 'Whisper To:\n%s'
ChatManagerCancel = lCancel
ChatManagerWhisperOffline = '%s is offline.'
OpenChatWarning = 'To become True Friends with somebody, click on them, and select "True Friends" from the detail panel.\n\nSpeedChat Plus can also be enabled, which allow users to chat by typing words found in the SpeedChat Plus dictionary.\n\nTo activate these features or to learn more, visit the Toontown Infinite website. Log in to edit your "Account Settings."\n'
OpenChatWarningOK = lOK
UnpaidChatWarning = 'Once you have subscribed, you can use this button to chat with your friends using the keyboard.  Until then, you should chat with other Toons using SpeedChat.'
UnpaidChatWarningPay = 'Subscribe'
UnpaidChatWarningContinue = 'Continue Free Trial'
PaidNoParentPasswordWarning = 'Use this button to chat with your friends by using the keyboard, enable it through your Account Manager on the Toontown Web site. Until then, you can chat by using SpeedChat.'
UnpaidNoParentPasswordWarning = 'This is for SpeedChat Plus, which allows users to chat by typing words found in the SpeedChat Plus dictionary. To activate this feature, exit Toontown and click on Membership. Select Manage Account and log in to edit your "Community Settings." If you are under 18, you need a Parent Account to manage these settings.'
PaidNoParentPasswordWarningSet = 'Update Chat Settings'
PaidNoParentPasswordWarningContinue = 'Continue Playing Game'
PaidParentPasswordUKWarning = 'Once you have Enabled Chat, you can enable this button to chat with your friends using the keyboard. Until then, you should chat with other Toons using SpeedChat.'
PaidParentPasswordUKWarningSet = 'Enable Chat Now!'
PaidParentPasswordUKWarningContinue = 'Continue Playing Game'
NoSecretChatWarningTitle = 'Parental Controls'
NoSecretChatWarning = 'To chat with a friend, the True Friends feature must first be enabled.  Kids, have your parent visit the Toontown Web site to learn about True Friends.'
RestrictedSecretChatWarning = 'To get or enter a True Friend Code, log in with the Parent Account. You can disable this prompt by changing your True Friends options.'
NoSecretChatWarningOK = lOK
NoSecretChatWarningCancel = lCancel
NoSecretChatWarningWrongPassword = "That's not the correct Parent Account.  Please log in with the Parent Account that is linked to this account."
NoSecretChatAtAllTitle = 'Open Chat With True Friends'
NoSecretChatAtAll = 'Open Chat with True Friends allows real-life friends to chat openly with each other by means of a True Friend Code that must be shared outside of the game.\n\nTo activate these features or to learn more, exit Toontown and then click on Membership and select Manage Account. Log in to edit your "Community Settings." If you are under 18, you need a Parent Account to manage these settings.'
NoSecretChatAtAllAndNoWhitelistTitle = 'Chat button'
NoSecretChatAtAllAndNoWhitelist = 'You can use the blue Chat button to communicate with other Toons by using Speechat Plus or Open Chat with True Friends.\n\nSpeedchat Plus is a form of type chat that allows users to communicate by using the SpeedChat Plus dictionary.\n\nOpen Chat with True Friends allows real-life friends to chat openly with each other by means of a True Friend Code that must be shared outside of the game.\n\nTo activate these features or to learn more, exit Toontown and then click on Membership and select Manage Account.  Log in to edit your "Community Settings." If you are under 18, you need a Parent Account to manage these settings.'
NoSecretChatAtAllOK = lOK
ChangeSecretFriendsOptions = 'Change True Friends Options'
ChangeSecretFriendsOptionsWarning = '\nPlease enter the Parent Account Password to change your True Friends options.'
ActivateChatTitle = 'True Friends Options'
WhisperToFormat = 'To %s %s'
WhisperToFormatName = 'To %s'
WhisperFromFormatName = '%s whispers'
ThoughtOtherFormatName = '%s thinks'
ThoughtSelfFormatName = 'You think'


propertyManager = TextPropertiesManager.getGlobalPtr()

shadow = TextProperties()
shadow.setShadow(-0.05, -0.05)
shadow.setShadowColor(0, 0, 0, 1)
propertyManager.setProperties('shadow', shadow)

white_shadow = TextProperties()
white_shadow.setShadow(-0.05, 0.05)
white_shadow.setShadowColor(1, 1, 1, 1)
propertyManager.setProperties('white_shadow', white_shadow)

TextColors = {
 'red': (1, 0, 0, 1),
 'green': (0, 1, 0, 1),
 'yellow': (1, 1, 0, 1),
 'midgreen': (0.2, 1, 0.2, 1),
 'blue': (0, 0, 1, 1),
 'white': (1, 1, 1, 1),
 'black': (0, 0, 0, 1),
 'grey': (0.5, 0.5, 0.5, 1),
 'gold': (1, 0.84, 0, 1),
 'brown': (0.8, 0.4, 0, 1),
 'orange': (1, 0.54, 0, 1),
 'darkGray': (0.2, 0.2, 0.2, 1),
 'darkPink': (0.75, 0.5, 0.85, 1),
 'darkGreen': (0, 0.45, 0, 1),
 'darkRed': (0.85, 0.15, 0.15, 1),
 'lightBlue': (0.4, 0.6, 1, 1),
 'skyBlue': (0, 0.6, 1, 1),
 'waterGreen': (0.2, 0.6, 0.3, 1),
 'beige': (1, 0.95, 0.7, 1),           # Light yellow
 'amber': (1, 0.75, 0, 1),             # Orange
 'amaranth': (0.9, 0.15, 0.3, 1),      # Pink
 'androidGreen': (0.65, 0.75, 0.2, 1), # Green
 'caribbeanGreen': (0, 0.8, 0.6, 1),   # Turquoise-green
 'azure': (0, 0.5, 1, 1),              # Blue
 'cobalt': (0, 0.3, 0.65, 1),          # Cobalt-blue
 'forestGreen': (0.15, 0.8, 0.15, 1)   # Forest-green
}

for name, color in TextColors.items():
    property = TextProperties()
    property.setTextColor(*color)
    propertyManager.setProperties(name, property)

ActivateChat = "True Friends allows one member to chat with another member only by means of a True Friend Code that must be communicated outside of the game. True Friends is not moderated or supervised.\n\nPlease choose one of Toontown's True Friends options:\n\n      \x01shadow\x01No True Friends\x02 - Ability to make True Friends is disabled.\n      This offers the highest level of control.\n\n      \x01shadow\x01Restricted True Friends\x02 - Requires the Parent Account Password to make\n      each new True Friend.\n\n      \x01shadow\x01Unrestricted True Friends\x02 - Once enabled with the Parent Account Password,\n      it is not required to supply the Parent Account Password to make each new\n      True Friend. \x01red\x01This option is not recommended for children under 13.\x02\n\n\n\n\n\n\nBy enabling the True Friends feature, you acknowledge that there are some risks inherent in the True Friends feature and that you have been informed of, and agree to accept, any such risks."
ActivateChatYes = 'Update'
ActivateChatNo = lCancel
ActivateChatMoreInfo = 'More Info'
ActivateChatPrivacyPolicy = 'Privacy Policy'
ActivateChatPrivacyPolicy_Button1A = 'Version 1'
ActivateChatPrivacyPolicy_Button1K = 'Version 1'
ActivateChatPrivacyPolicy_Button2A = 'Version 2'
ActivateChatPrivacyPolicy_Button2K = 'Version 2'
PrivacyPolicyText_1A = [' ']
PrivacyPolicyText_1K = [' ']
PrivacyPolicyText_2A = [' ']
PrivacyPolicyText_2K = [' ']
PrivacyPolicyText_Intro = [' ']
PrivacyPolicyClose = lClose
SecretFriendsInfoPanelOk = lOK
SecretFriendsInfoPanelClose = lClose
SecretFriendsInfoPanelText = ['\nThe Open Chat with True Friends Feature\n\nThe Open Chat with True Friends feature enables a member to chat directly with another member within Toontown Infinite (the "Service") once the members establish a True Friends connection.  When your child attempts to use the Open Chat with True Friends feature, we will require that you indicate your consent to your child\'s use of this feature by entering your Parent Account Password.  Here is a detailed description of the process of creating an Open Chat with True Friends connection between members whom we will call "Sally" and "Mike."\n1. Sally\'s parent and Mike\'s parent each enable the Open Chat with True Friends feature by entering their respective Parent Account Passwords either (a) in the Account Options areas within the Service, or (b) when prompted within the game by a Parental Controls pop-up.\n2. Sally requests a True Friend Code (described below) from within the Service.\n',
 "\n3. Sally's True Friend Code is communicated to Mike outside of the Service. (Sally's True Friend Code may be communicated to Mike either directly by Sally, or indirectly through Sally's disclosure of the True Friend Code to another person.)\n4. Mike submits Sally's True Friend Code to the Service within 48 hours of the time that Sally requested the True Friend Code from the Service.\n5. The Service then notifies Mike that Sally has become Mike's True Friend.  The Service similarly notifies Sally that Mike has become Sally's True Friend.\n6. Sally and Mike can now open chat directly with each other until either one chooses to terminate the other as a True Friend, or until the Open Chat with True Friends feature is disabled for either Sally or Mike by their respective parent.  The True Friends connection can thus be disabled anytime by either: (a) a member removing the True Friend from his or her friends list (as described in the Service); or, (b) the parent of that member disabling the Open Chat with ",
 "\nTrue Friends feature by going to the Account Options area within the Service and following the steps set forth there.\n\nA True Friend Code is a computer-generated random code assigned to a particular member. The True Friend Code must be used to activate a True Friend connection within 48 hours of the time that the member requests the True Friend Code; otherwise, the True Friend Code expires and cannot be used.  Moreover, a single True Friend Code can only be used to establish one True Friend connection.  To make additional True Friend connections, a member must request an additional True Friend Code for each additional True Friend.\n\nTrue Friendships do not transfer.  For example, if Sally becomes a True Friend of Mike, and Mike becomes a True Friend of Jessica, Sally does not automatically become Jessica's True Friend.  In order for Sally and Jessica to\n",
 '\nbecome True Friends, one of them must request a new True Friend Code from the Service and communicate it to the other.\n\nTrue Friends communicate with one another in a free-form interactive open chat.  The content of this chat is directly entered by the participating member and is processed through the Service, which is monitored by the Toontown Infinite team.  While we advise members not to exchange personal information such as first and last names, e-mail addresses, postal addresses, or phone numbers while using Open Chat with True Friends, we cannot guarantee that such exchanges of personal information will not happen. Although the True Friends chat is automatically filtered for most bad words, Open Chat with True Friends may be moderated, and we reserve the right to moderate any part of the Service that we,\n',
 "\nin our sole and absolute discretion, deems necessary. However, because Open Chat with True Friends will not always be moderated, if the Parent Account allows a child to use his or her account with the Open Chat with True Friends feature enabled, we strongly encourage parents to supervise their child or children while they play in the Service. By enabling the Open Chat with True Friends feature, the Parent Account acknowledges that there are some risks inherent in the Open Chat with True Friends feature and that the Parent Account has been informed of, and agrees to accept, any such risks, whether foreseeable or otherwise. \n\nWDIG does not use the content of True Friends chat for any purpose other than communicating that content to the member's true friend, and does not disclose that content to any third party except: (1) if required by law, for example, to comply with a court order or subpoena; (2) to enforce the Terms of Use\n",
 "\napplicable to the Service (which may be accessed on the home page of the Service); or, (3) to protect the safety and security of Members of the Service and the Service itself. In accordance with the Children's Online Privacy Protection Act, we are prohibited from conditioning, and do not condition, a child's participation in any activity (including Open Chat with True Friends) on the child's disclosing more personal information than is reasonably necessary to participate in such activity.\n\nIn addition, as noted above, we recognize the right of a parent to refuse to permit us to continue to allow a child to use the True Friends feature. By enabling the Open Chat with True Friends feature, you acknowledge that there are some risks inherent in the ability of members to open chat with one another through the Open Chat with True Friends feature, and that you have been informed of, and agree to accept, any such risks, whether foreseeable or otherwise.\n"]
LeaveToPay = 'Click Purchase to exit the game and buy a Membership at toontown.com'
LeaveToPayYes = 'Purchase'
LeaveToPayNo = lCancel
LeaveToSetParentPassword = 'In order to set parent account password, the game will exit to the Toontown website.'
LeaveToSetParentPasswordYes = 'Set Password'
LeaveToSetParentPasswordNo = lCancel
LeaveToEnableChatUK = 'In order to enable chat, the game will exit to the Toontown website.'
LeaveToEnableChatUKYes = 'Enable Chat'
LeaveToEnableChatUKNo = lCancel
ChatMoreInfoOK = lOK
SecretChatDeactivated = 'The "True Friends" feature has been disabled.'
RestrictedSecretChatActivated = 'The "Restricted True Friends" feature has been enabled!'
SecretChatActivated = 'The "Unrestricted True Friends" feature has been enabled!'
SecretChatActivatedOK = lOK
SecretChatActivatedChange = 'Change Options'
ProblemActivatingChat = 'Oops!  We were unable to activate the "True Friends" chat feature.\n\n%s\n\nPlease try again later.'
ProblemActivatingChatOK = lOK
MultiPageTextFrameNext = lNext
MultiPageTextFramePrev = 'Previous'
MultiPageTextFramePage = 'Page %s/%s'
GuiScreenToontownUnavailable = 'The server appears to be temporarily unavailable, still trying...'
GuiScreenCancel = lCancel
CreateAccountScreenUserName = 'Account Name'
CreateAccountScreenPassword = 'Password'
CreateAccountScreenConfirmPassword = 'Confirm Password'
CreateAccountScreenCancel = lCancel
CreateAccountScreenSubmit = 'Submit'
CreateAccountScreenConnectionErrorSuffix = '.\n\nPlease try again later.'
CreateAccountScreenNoAccountName = 'Please enter an account name.'
CreateAccountScreenAccountNameTooShort = 'Your account name must be at least %s characters long. Please try again.'
CreateAccountScreenPasswordTooShort = 'Your password must be at least %s characters long. Please try again.'
CreateAccountScreenPasswordMismatch = 'The passwords you typed did not match. Please try again.'
CreateAccountScreenUserNameTaken = 'That user name is already taken. Please try again.'
CreateAccountScreenInvalidUserName = 'Invalid user name.\nPlease try again.'
CreateAccountScreenUserNameNotFound = 'User name not found.\nPlease try again or create a new account.'
CRConnecting = 'Connecting...'
CRNoConnectTryAgain = 'Could not connect to %s:%s. Try again?'
CRNoConnectProxyNoPort = 'Could not connect to %s:%s.\n\nYou are communicating to the internet via a proxy, but your proxy does not permit connections on port %s.\n\nYou must open up this port, or disable your proxy, in order to play.  If your proxy has been provided by your ISP, you must contact your ISP to request them to open up this port.'
CRMissingGameRootObject = 'Missing some root game objects.  (May be a failed network connection).\n\nTry again?'
CRNoDistrictsTryAgain = 'No Districts are available. Try again?'
CRRejectRemoveAvatar = 'The avatar was not able to be deleted, try again another time.'
CRLostConnection = 'The connection to the server has been closed.'
CRBootedReasons = {
 1: 'An unexpected problem has occurred.  Your connection has been lost, but you should be able to connect again and go right back into the game.',
 100: 'You have been disconnected because someone else just logged in using your account on another computer.',
 120: 'You have been disconnected because of a problem with your authorization to use keyboard chat.',
 122: 'Authentication failed.',
 124: 'The install files on your computer and/or the server you are trying to connect to are out of date.  To download the latest Toontown Infinite version, be sure to start the game with the official launcher.  If you continue to get this error, contact support.',
 125: 'Your installed files appear to be invalid.  Please use the Play button on the official website to run.',
 126: 'You are not authorized to use administrator privileges.',
 127: 'A problem has occurred with your Toon.  Please contact Member Services via phone or email and reference Error Code 127.  Thank you.',
 151: "Your account details have been modified.",
 152: "You have been banned from this server. For more details, please contact the host.\nYou may continue playing Toontown Infinite in Singleplayer or on another server. Try improving your behavior to avoid any other bans.",
 153: 'The district you were playing on has been reset.  Everyone who was playing on that district has been disconnected.  However, you should be able to connect again and go right back into the game.',
 154: 'Toontown Infinite has been temporarily closed for scheduled downtime. Everyone who was playing on the Kaldron Network has been disconnected from the game.\n\nIf you wish to continue playing, you may go into custom play until maintenance is complete.\n\nFor more information, please visit the Toontown Infinite website.',
 288: 'Sorry, you have used up all of your available minutes this month.',
 349: 'Sorry, you have used up all of your available minutes this month.',
 420: 'Sorry, you cannot connect to a server with cooperative play disabled.'
}
CRBootedReasonUnknownCode = 'An unexpected problem has occurred (error code %s).  Your connection has been lost, but you should be able to connect again and go right back into the game.'
CRTryConnectAgain = '\n\nTry to connect again?'
CRToontownUnavailable = 'The server appears to be temporarily unavailable, still trying...'
CRToontownUnavailableCancel = lCancel
CRNameCongratulations = 'CONGRATULATIONS!!'
CRNameAccepted = 'Your name has been\napproved by the Toon Council.\n\nFrom this day forth\nyou will be named\n"%s"'
CRServerConstantsProxyNoPort = 'Unable to contact %s.\n\nYou are communicating to the internet via a proxy, but your proxy does not permit connections on port %s.\n\nYou must open up this port, or disable your proxy, in order to play.  If your proxy has been provided by your ISP, you must contact your ISP to request them to open up this port.'
CRServerConstantsProxyNoCONNECT = 'Unable to contact %s.\n\nYou are communicating to the internet via a proxy, but your proxy does not support the CONNECT method.\n\nYou must enable this capability, or disable your proxy, in order to play.  If your proxy has been provided by your ISP, you must contact your ISP to request them to enable this capability.'
CRServerConstantsTryAgain = 'Unable to contact %s.\n\nThe account server might be temporarily down, or there might be some problem with your internet connection.\n\nTry again?'
CRServerDateTryAgain = 'Could not get server date from %s. Try again?'
CRMaintenanceCountdownMessage = 'Attention Toons! Toontown Infinite will be going down for maintenance in %d minutes.'
CRMaintenanceMessage = 'Attention Toons! Toontown Infinite is now going down for maintenance.'
AfkForceAcknowledgeMessage = 'Your toon got sleepy and went to bed.'
PeriodTimerWarning = 'Your available time is almost over!'
PeriodForceAcknowledgeMessage = 'Sorry, you have used up all of your available time. Please exit to purchase more.'
CREnteringToontown = 'Entering...'
DownloadWatcherUpdate = 'Downloading %s'
DownloadWatcherInitializing = 'Download Initializing...'
LoginScreenUserName = 'Account Name'
LoginScreenPassword = 'Password'
LoginScreenLogin = 'Login'
LoginScreenCreateAccount = 'Create Account'
LoginScreenQuit = lQuit
LoginScreenLoginPrompt = 'Please enter a user name and password.'
LoginScreenBadPassword = 'Bad password.\nPlease try again.'
LoginScreenInvalidUserName = 'Invalid user name.\nPlease try again.'
LoginScreenUserNameNotFound = 'User name not found.\nPlease try again or create a new account.'
LoginScreenPeriodTimeExpired = 'Sorry, you have used up all of your available time.'
LoginScreenNoNewAccounts = 'Sorry, we are not accepting new accounts at this time.'
LoginScreenTryAgain = 'Try Again'
DialogSpecial = 'ooo'
DialogExclamation = '!'
DialogQuestion = '?'
DialogLength1 = 6
DialogLength2 = 12
DialogLength3 = 20
SCMenuPromotion = 'PROMOTIONAL'
SCMenuEmotions = 'EMOTIONS'
SCMenuCustom = 'MY PHRASES'
SCMenuResistance = 'UNITE!'
SCMenuPets = 'PETS'
SCMenuPetTricks = 'TRICKS'
SCMenuCog = 'COG SPEAK'
SCMenuHello = 'HELLO'
SCMenuBye = 'GOODBYE'
SCMenuConvo = 'CHIT CHAT'
SCMenuEmoticons = 'EMOTICONS'
SCMenuResponse="REPLIES"
SCMenuGood = 'GOOD'
SCMenuBad = 'BAD'
SCMenuHappy = 'HAPPY'
SCMenuSad = 'SAD'
SCMenuFriendly = 'FRIENDLY'
SCMenuSorry = 'SORRY'
SCMenuBusy = "I'M BUSY..."
SCMenuStinky = 'STINKY'
SCMenuPlaces = 'PLACES'
SCMenuToontasks = 'TOONTASKS'
SCMenuBattle = 'BATTLE'
SCMenuBattleUse = 'YOU SHOULD USE...'
SCMenuBattleToonUp = 'TOON-UP'
SCMenuBattleTrap = 'TRAP'
SCMenuBattleLure = 'LURE'
SCMenuBattleSound = 'SOUND'
SCMenuBattleThrow = 'THROW'
SCMenuBattleSquirt = 'SQUIRT'
SCMenuBattleDrop = 'DROP'
SCMenuGagShop = 'TROLLEY'
SCMenuFactory = 'FACTORY'
SCMenuCogGolf = 'COUNTRY CLUB'
SCMenuKartRacing = 'RACING'
SCMenuFactoryMeet = 'MEET'
SCMenuCFOBattle = 'C.F.O.'
SCMenuCFOBattleCranes = 'CRANES'
SCMenuCFOBattleGoons = 'GOONS'
SCMenuCJBattle = 'CHIEF JUSTICE'
SCMenuCEOBattle = 'C.E.O.'
SCMenuGolf = 'GOLF'
SCMenuWhiteList = 'WHITELIST'
SCMenuPlacesPlayground = 'PLAYGROUND'
SCMenuPlacesEstate = 'ESTATE'
SCMenuPlacesCogs = 'COGS'
SCMenuPlacesWait = 'WAIT'
SCMenuFriendlyYou = 'YOU...'
SCMenuFriendlyILike = 'I LIKE YOUR...'
SCMenuPlacesLetsGo = "LET'S GO..."
SCMenuToontasksMyTasks = 'MY TASKS'
SCMenuToontasksYouShouldChoose = 'I THINK YOU SHOULD...'
SCMenuToontasksINeedMore = 'I NEED MORE...'
SCMenuBattleGags = 'GAGS'
SCMenuBattleTaunts = 'TAUNTS'
SCMenuBattleStrategy = 'STRATEGY'
SCMenuBoardingGroup = 'BOARDING'
SCMenuParties = 'PARTIES'
SCMenuAprilToons = "APRIL TOONS'"
SCMenuSingingGroup = 'SINGING'
SCMenuCarol = 'CAROLING'
SCMenuSillyHoliday = 'SILLY METER'
SCMenuVictoryParties = 'VICTORY PARTIES'
SCMenuSellbotNerf = 'STORM SELLBOT'
SCMenuJellybeanJam = 'JELLYBEAN WEEK'
SCMenuHalloween = 'HALLOWEEN'
SCMenuWinter = 'WINTER'
SCMenuSellbotInvasion = 'SELLBOT INVASION'
SCMenuFieldOffice = 'FIELD OFFICES'
SCMenuIdesOfMarch = 'GREEN'
FriendSecretNeedsPasswordWarningTitle = 'Parental Controls'
FriendSecretNeedsParentLoginWarning = 'To get or enter a True Friend Code, log in with the Parent Account.  You can disable this prompt by changing your True Friend options.'
FriendSecretNeedsPasswordWarning = 'To get or enter a True Friend Code, you must enter the Parent Account Password.  You can disable this prompt by changing your True Friends options.'
FriendSecretNeedsPasswordWarningOK = lOK
FriendSecretNeedsPasswordWarningCancel = lCancel
FriendSecretNeedsPasswordWarningWrongUsername = "That's not the correct username.  Please enter the username of the parental account.  This is not the same username used to play the game."
FriendSecretNeedsPasswordWarningWrongPassword = "That's not the correct password.  Please enter the password of the parental account.  This is not the same password used to play the game."
FriendSecretIntro = "If you wish to use the unrestricted chat feature with close friends, you can become True Friends! Other Toons won't see the unrestricted chat unless they are also your True Friend.\n\nTo start, get a True Friend Code. Tell the True Friend Code to your friend, but not to anyone else. When your friend types in your True Friend Code on his or her screen, you'll be True Friends in Toontown!"
FriendSecretGetSecret = 'Get a True Friend Code'
FriendSecretEnterSecret = 'If you have a True Friend Code from someone you know, type it here.'
FriendSecretOK = lOK
FriendSecretEnter = 'Enter True Friend Code'
FriendSecretCancel = lCancel
FriendSecretGettingSecret = 'Getting True Friend Code. . .'
FriendSecretGotSecret = "Here is your new True Friend Code. Be sure to write it down!\n\nYou may give this True Friend Code to one person only. Once someone types in your True Friend Code, it will not work for anyone else.  If you want to give a True Friend Code to more than one person, get another True Friend Code.\n\nThe True Friend Code will only work for the next two days.  Your friend will have to type it in before it goes away, or it won't work.\n\nYour True Friend Code is:"
FriendSecretTooMany = "Sorry, you can't have any more True Friend Codes today.  You've already had more than your fair share!\n\nTry again tomorrow."
FriendSecretTryingSecret = 'Trying True Friend Code. . .'
FriendSecretNotImplemented = 'True Friends has not been implemented yet!'
FriendSecretEnteredSecretSuccess = 'You are now True Friends with %s!\nYou may now talk to this Toon using the unrestricted chat.'
FriendSecretTimeOut = 'Sorry, secrets are not working right now.'
FriendSecretEnteredSecretUnknown = "That's not anyone's True Friend Code.  Are you sure you spelled it correctly?\n\nIf you did type it correctly, it may have expired.  Ask your friend to get a new True Friend Code for you (or get a new one yourself and give it to your friend)."
FriendSecretEnteredSecretFull = "You can't be friends with %s because one of you has too many friends on your friends list."
FriendSecretEnteredSecretFullNoName = "You can't be friends because one of you has too many friends on your friends list."
FriendSecretEnteredSecretSelf = 'You just typed in your own True Friend Code!  Now no one else can use that True Friend Code.'
FriendSecretEnteredSecretWrongProduct = "You have entered the wrong type of True Friend Code.\nThis game uses codes that begin with '%s'."
FriendSecretNowFriends = 'You are now True Friends with %s!'
FriendSecretNowFriendsNoName = 'You are now True Friends!'
FriendSecretDetermineSecret = 'What type of True Friend would you like to make?'
FriendSecretDetermineSecretAvatar = 'Avatar'
FriendSecretDetermineSecretAvatarRollover = 'A friend only in this game'
FriendSecretDetermineSecretAccount = 'Account'
FriendSecretDetermineSecretAccountRollover = 'A friend across the Toontown Infinite network'
GuildMemberTitle = 'Member Options'
GuildMemberPromote = 'Make Officer'
GuildMemberPromoteInvite = 'Make Veteran'
GuildMemberDemoteInvite = 'Demote to Veteran'
GuildMemberGM = 'Make Guildmaster'
GuildMemberGMConfirm = 'Confirm'
GuildMemberDemote = 'Demote to Member'
GuildMemberKick = 'Remove Member'
GuildMemberCancel = lCancel
GuildMemberOnline = 'has come online.'
GuildMemberOffline = 'has gone offline.'
GuildPrefix = '(G):'
GuildNewMember = 'New Guild Member'
GuildMemberUnknown = 'Unknown'
GuildMemberGMMessage = 'Warning! Would you like to give up leadership of your guild and make %s your guild master?\n\nYou will become an officer'
GuildInviteeOK = lOK
GuildInviteeNo = lNo
GuildInviteeInvitation = '%s is inviting you to join %s.'
GuildRedeemErrorInvalidToken = 'Sorry, that code is invalid. Please try again.'
GuildRedeemErrorGuildFull = 'Sorry, this guild has too many members already.'
FriendInviteeTooManyFriends = '%s would like to be your friend, but you already have too many friends on your list!'
FriendInviteeInvitation = '%s would like to be your friend.'
FriendInviteeInvitationPlayer = "%s's player would like to be your friend."
FriendNotifictation = '%s is now your friend.'
FriendInviteeOK = lOK
FriendInviteeNo = lNo
GuildInviterWentAway = '%s is no longer present.'
GuildInviterAlready = '%s is already in a guild.'
GuildInviterBusy = '%s is busy right now.'
GuildInviterNotYet = 'Invite %s to join your guild?'
GuildInviterCheckAvailability = 'Inviting %s to join your guild.'
GuildInviterOK = lOK
GuildInviterNo = lNo
GuildInviterCancel = lCancel
GuildInviterYes = lYes
GuildInviterTooFull = 'Guild has reached maximum size.'
GuildInviterClickToon = 'Click on the pirate you would like to invite.'
GuildInviterTooMany = 'This is a bug'
GuildInviterNotAvailable = '%s is busy right now; try again later.'
GuildInviterGuildSaidNo = '%s has declined your guild invitation.'
GuildInviterAlreadyInvited = '%s has already been invited.'
GuildInviterEndGuildship = 'Remove %s from the guild?'
GuildInviterFriendsNoMore = '%s has left the guild.'
GuildInviterSelf = 'You are already in the guild!'
GuildInviterIgnored = '%s is ignoring you.'
GuildInviterAsking = 'Asking %s to join the guild.'
GuildInviterGuildSaidYes = '%s has joined the guild!'
GuildInviterFriendKickedOut = '%s has kicked out %s from the Guild.'
GuildInviterFriendKickedOutP = '%s have kicked out %s from the Guild.'
GuildInviterFriendInvited = '%s has invited %s to the Guild.'
GuildInviterFriendInvitedP = '%s have invited %s to the Guild.'
GuildInviterFriendPromoted = '%s has promoted %s to the rank of %s.'
GuildInviterFriendPromotedP = '%s have promoted %s to the rank of %s.'
GuildInviterFriendDemoted = '%s has demoted %s to the rank of %s.'
GuildInviterFriendDemotedP = '%s have demoted %s to the rank of %s.'
GuildInviterFriendPromotedGM = '%s has named %s as the new %s'
GuildInviterFriendPromotedGMP = '%s have named %s as the new %s'
GuildInviterFriendDemotedGM = '%s has been named by %s as the new GuildMaster who became the rank of %s'
GuildInviterFriendDemotedGMP = '%s have been named by %s as the new GuildMaster who beaome the rank of %s'
FriendOnline = 'has come online.'
FriendOffline = 'has gone offline.'
FriendInviterOK = lOK
FriendInviterCancel = lCancel
FriendInviterStopBeingFriends = 'Stop being friends'
FriendInviterConfirmRemove = 'Remove'
FriendInviterYes = lYes
FriendInviterNo = lNo
FriendInviterClickToon = 'Click on the Toon you would like to make friends with.'
FriendInviterTooMany = 'You have too many friends on your list to add another one now. You will have to remove some friends if you want to make friends with %s.'
FriendInviterToonTooMany = 'You have too many Toon friends on your list to add another one now. You will have to remove some Toon friends if you want to make friends with %s.'
FriendInviterPlayerTooMany = 'You have too many player friends on your list to add another one now. You will have to remove some player friends if you want to make friends with %s.'
FriendInviterNotYet = 'Would you like to make friends with %s?'
FriendInviterCheckAvailability = 'Seeing if %s is available.'
FriendInviterNotAvailable = '%s is busy right now; try again later.'
FriendInviterCantSee = 'This only works if you can see %s.'
FriendInviterNotOnline = 'This only works if %s is online'
FriendInviterNotOpen = '%s does not have open chat, use secrets to make friends'
FriendInviterWentAway = '%s went away.'
FriendInviterAlready = '%s is already your friend.'
FriendInviterAlreadyInvited = '%s has already been invited.'
FriendInviterAskingCog = 'Asking %s to be your friend.'
FriendInviterAskingPet = '%s jumps around, runs in circles and licks your face.'
FriendInviterAskingMyPet = '%s is already your BEST friend.'
FriendInviterEndFriendship = 'Are you sure you want to stop being friends with %s?'
FriendInviterFriendsNoMore = '%s is no longer your friend.'
FriendInviterSelf = "You are already 'friends' with yourself!"
FriendInviterIgnored = '%s is ignoring you.'
FriendInviterAsking = 'Asking %s to be your friend.'
FriendInviterFriendSaidYes = 'You are now friends with %s!'
FriendInviterPlayerFriendSaidYes = "You are now friends with %s's player, %s!"
FriendInviterFriendSaidNo = '%s has declined your friend request.'
FriendInviterCannotFriend = 'Your friend request could not be sent.'
FriendInviterFriendSaidNoNewFriends = "%s isn't looking for new friends right now."
FriendInviterOtherTooMany = '%s has too many friends already!'
FriendInviterMaybe = '%s was unable to answer.'
FriendInviterDown = 'Cannot make friends now.'
TalkGuild = 'G'
TalkParty = 'P'
TalkPVP = 'PVP'
AntiSpamInChat = '***Spamming***'
IgnoreConfirmOK = lOK
IgnoreConfirmCancel = lCancel
IgnoreConfirmYes = lYes
IgnoreConfirmNo = lNo
IgnoreConfirmNotYet = 'Would you like to Ignore %s?'
IgnoreConfirmAlready = 'You are already ignoring %s.'
IgnoreConfirmSelf = 'You cannot ignore yourself!'
IgnoreConfirmNewIgnore = 'You are ignoring %s.'
IgnoreConfirmEndIgnore = 'You are no longer ignoring %s.'
IgnoreConfirmRemoveIgnore = 'Stop ignoring %s?'
EmoteWhispers = ['%s waves.',
 '%s is happy.',
 '%s is sad.',
 '%s is angry.',
 '%s is sleepy.',
 '%s shrugs.',
 '%s dances.',
 '%s thinks.',
 '%s is bored.',
 '%s applauds.',
 '%s cringes.',
 '%s is confused.',
 '%s does a belly flop.',
 '%s bows to you.',
 '%s slips on a banana peel.',
 '%s gives the resistance salute.',
 '%s laughs.',
 "%s says '" + lYes + "'.",
 "%s says '" + lNo + "'.",
 "%s says '" + lOK + "'.",
 '%s is surprised.',
 '%s is crying.',
 '%s is delighted.',
 '%s is furious.',
 '%s is laughing.',
 '%s taunts you.']
SpeedChatStaticTextPirates = {50001: 'Aye',
 50002: 'Nay',
 50003: 'Yes',
 50004: 'No',
 50005: 'Ok',
 50100: 'Gangway!',
 50101: 'Blimey!',
 50102: 'Well blow me down!',
 50103: 'Walk the plank!',
 50104: 'Dead men tell no tales....',
 50105: 'Shiver me timbers!',
 50106: "Salty as a Kraken's kiss.",
 50107: 'Treasure be the measure of our pleasure!',
 50108: "I don't fear death - I attune it.",
 50700: 'Ahoy!',
 50701: 'Ahoy, mate!',
 50702: 'Yo-Ho-Ho',
 50703: 'Avast!',
 50704: 'Hey Bucko.',
 50800: 'Until next time.',
 50801: 'May fair winds find ye.',
 50802: 'Godspeed.',
 50900: 'How are ye, mate?',
 50901: '',
 51000: "It's like the sky is raining gold doubloons!",
 51001: 'May a stiff wind be at our backs, the sun on our faces and our cannons fire true!',
 51100: 'I be sailing some rough waters today.',
 51200: 'Me apologies, mate.',
 51201: 'Sorry.',
 51202: 'Sorry, I was busy before.',
 51203: 'Sorry, I already have plans.',
 51204: "Sorry, I don't need to do that.",
 51300: 'Attack the weakest one!',
 51301: 'Attack the strongest one!',
 51302: 'Attack me target!',
 51303: 'I be needing help!',
 51304: "I can't do any damage!",
 51305: 'I think we be in trouble.',
 51306: 'Surround the most powerful one.',
 51307: 'We should retreat.',
 51308: 'Run for it!',
 51400: 'Fire a Broadside!',
 51401: 'Port Side! (left)',
 51402: 'Starboard Side! (right)',
 51403: 'Incoming!',
 51404: 'Come about!',
 51405: 'Broadside! Take Cover!',
 51406: 'To the Cannons!',
 51407: 'Open fire!',
 51408: 'Hold yer fire!',
 51409: 'Aim for the masts!',
 51410: 'Aim for the hull!',
 51411: 'Prepare to board!',
 51412: "She's coming about.",
 51413: 'Ramming speed!',
 51414: "We've got her on the run.",
 51415: 'We be taking on water!',
 51416: "We can't take anymore!",
 51417: "I don't have a shot!",
 51418: "Let's find port for repair.",
 51419: 'Man overboard!',
 51420: 'Enemy spotted.',
 51421: 'Handsomely now, mates!',
 50400: "Let's set sail.",
 50401: "Let's get out of here.",
 51500: "Let's sail to Port Royal.",
 51501: "Let's sail to Tortuga.",
 51502: "Let's sail to Padres Del Fuego.",
 51503: "Let's sail to Devil's Anvil.",
 51504: "Let's sail to Kingshead.",
 51505: "Let's sail to Isla Perdida.",
 51506: "Let's sail to Cuba.",
 51507: "Let's sail to Tormenta.",
 51508: "Let's sail to Outcast Isle.",
 51509: "Let's sail to Driftwood.",
 51510: "Let's sail to Cutthroat.",
 51511: "Let's sail to Rumrunner's Isle.",
 51512: "Let's sail to Isla Cangrejos.",
 51600: "Let's head into town.",
 51601: "Let's go to the docks.",
 51602: "Let's head to the tavern.",
 51800: "Let's go to Fort Charles.",
 51801: "Let's go to the Governor's Mansion.",
 52500: 'Where be I, mate?',
 51700: 'Yer already there.',
 51701: "I don't know.",
 51702: 'Yer on the wrong island.',
 51703: "That's in town.",
 51704: 'Look just outside of town.',
 51705: 'Ye will have to search through the jungle.',
 51706: 'Deeper inland.',
 51707: 'Oh, that be by the coast.',
 50200: 'Bilge rat!',
 50201: 'Scurvy dog!',
 50202: 'See ye in Davy Jones locker!',
 50203: 'Scoundrel!',
 50204: 'Landlubber!',
 50205: 'Addle-minded fool!',
 50206: 'You need a sharp sword and sharper wits.',
 50207: 'Ye be one doubloon short of a full hull mate!',
 50208: "Watch yer tongue or I'll pickle it with sea salt!",
 50209: 'Touch me loot and you get the boot!',
 50210: 'The horizon be as empty as yer head.',
 50211: "You're a canvas shy of a full sail, aren't ye mate?",
 50300: 'Fine shooting mate!',
 50301: 'A well placed blow!',
 50302: 'Nice shot!',
 50303: 'Well met!',
 50304: 'We showed them!',
 50305: 'Yer not so bad yerself!',
 50306: 'A fine plunder haul!',
 52400: 'May luck be my lady.',
 52401: 'I think these cards be marked!',
 52402: 'Blimey cheater!',
 51900: "That's a terrible flop!",
 51901: 'Trying to buy the hand, are ye?',
 51902: 'Ye be bluffing.',
 51903: "I don't think ye had it.",
 51904: 'Saved by the river.',
 52600: 'Hit me.',
 52601: 'Can I get another dealer?',
 53101: 'I caught a fish!',
 53102: 'I saw a Legendary Fish!',
 53103: 'What did you catch?',
 53104: 'This will make a whale of a tale!',
 53105: 'That was a beauty!',
 53106: 'Arr, the sea is treacherous today.',
 53107: 'What a bountiful haul of fish!',
 53110: 'Do you have the Legendary Lure?',
 53111: 'Have you ever caught a Legendary Fish?',
 53112: 'Can you sail on a fishing boat?',
 53113: 'Where is the Fishing Master?',
 53114: 'Have you completed your fish collection?',
 53120: 'Fire at my target!',
 53121: 'Fire at the ship closest to the shore!',
 53122: "There's a ship getting away!",
 53123: 'Fire at the big ships!',
 53124: 'Fire at the small ships!',
 53125: 'More are coming!',
 53126: "We're not going to last much longer!",
 53127: 'Shoot the barrels!',
 53128: "We've got new ammo!",
 53129: 'Sturdy defense, mates!',
 53141: 'Look at the potion I made!',
 53142: 'Have you completed your potion collection?',
 53143: 'Where is the Gypsy?',
 53144: 'What potion is that?',
 53145: 'This potion was easy enough.',
 53146: "This potion was hard brewin', I tell ye!",
 53160: 'We need someone to bilge pump!',
 53161: 'We need someone to scrub!',
 53162: 'We need someone to saw!',
 53163: 'We need someone to brace!',
 53164: 'We need someone to hammer!',
 53165: 'We need someone to patch!',
 53166: "I'll do it!",
 53167: "Keep it up, this ship won't repair itself!",
 53168: 'Great job repairing the ship!',
 52100: 'Want to group up?',
 52101: 'Join me crew?',
 52200: 'Fight some skeletons?',
 52201: 'Fight some crabs?',
 52300: "How 'bout a game of Mayhem?",
 52301: 'Join me Mayhem game.',
 52302: 'Want to start a Mayhem game?',
 52303: 'Want to start a team battle game?',
 52304: 'Join me team battle game.',
 52350: 'Join my Cannon Defense.',
 52351: 'Want to start a Cannon Defense?',
 52352: 'Can you lend me a hand with Repair?',
 52353: 'We need to Repair the ship now!',
 52354: 'Care to catch some fish?',
 52355: 'Want to go fishing with me?',
 52356: "Join me crew for some fishin'?",
 52357: 'Time to brew some potions!',
 52358: 'You should try your hand at brewing potions.',
 52000: '',
 52000: '',
 52700: '',
 53000: '',
 52800: '',
 52900: '',
 50500: '',
 50600: '',
 60100: 'Hi!',
 60101: 'Hello!',
 60102: 'Hey!',
 60103: 'Yo!',
 60104: 'Hi everybody!',
 60105: 'How are you doing?',
 60106: "What's Up?",
 60200: 'Bye!',
 60201: 'Later!',
 60202: 'See ya!',
 60203: "I'll be right back.",
 60204: 'I need to go.',
 60300: ':-)',
 60301: 'Cool!',
 60302: 'Yeah!',
 60303: 'Ha ha!',
 60304: 'Sweet!',
 60305: 'Yeah!',
 60306: 'That rocks!',
 60307: 'Funky!',
 60308: 'Awesome!',
 60309: 'Wow!',
 60400: ':-(',
 60401: 'Doh!',
 60402: 'Aw man!',
 60403: 'Ouch!',
 60404: 'Bummer!',
 60500: 'Where are you?',
 60501: "Let's go to the Gateway Store.",
 60502: "Let's go to the Disco Hall.",
 60503: "Let's go to Toontown.",
 60504: "Let's go to Pirates of the Carribean.",
 60505: 'Flip coin',
 60506: 'Dance',
 60507: 'Chant 1',
 60508: 'Chant 2',
 60509: 'Dance a jig',
 60510: 'Sleep',
 60511: 'Flex',
 60512: 'Play Lute',
 60513: 'Play Flute',
 60514: 'Frustrated',
 60515: 'Searching',
 60516: 'Yawn',
 60517: 'Kneel',
 60518: 'Sweep',
 60519: 'Primp',
 60520: 'Yawn',
 60521: 'Dance',
 60522: 'No',
 60523: 'Yes',
 60524: 'Laugh',
 60525: 'Clap',
 60526: 'Smile',
 60527: 'Anger',
 60528: 'Fear',
 60529: 'Sad',
 60530: 'Celebrate',
 60668: 'Celebrate',
 60669: 'Sleep',
 60602: 'Angry',
 60614: 'Clap',
 60622: 'Scared',
 60640: 'Laugh',
 60652: 'Sad',
 60657: 'Smile',
 60664: 'Wave',
 60665: 'Wink',
 60666: 'Yawn',
 60669: 'Sleep',
 60670: 'Dance',
 60676: 'Flirt',
 60677: 'Zombie dance',
 60678: 'Noisemaker',
 60671: "Hello, I'm a Pirate, and I'm here to steal your heart.",
 60672: "I just found the treasure I've been searching for.",
 60673: "If you were a booger, I'd pick you first.",
 60674: 'Come to Tortuga often?',
 60675: 'Do you have a map?  I just keep getting lost in your eyes.',
 65000: 'Yes',
 65001: 'No',
 60909: 'Check Hand'}
Emotes_Root = 'EMOTES'
Emotes_Dances = 'Dances'
Emotes_General = 'General'
Emotes_Music = 'Music'
Emotes_Expressions = 'Emotions'
Emote_ShipDenied = 'Cannot emote while sailing.'
Emote_MoveDenied = 'Cannot emote while moving.'
Emote_CombatDenied = 'Cannot emote while in combat.'
Emote_CannonDenied = 'Cannot emote while using a cannon.'
Emote_SwimDenied = 'Cannot emote while swimming.'
Emote_ParlorGameDenied = 'Cannot emote while playing a parlor game.'
Emotes = (60505,
 60506,
 60509,
 60510,
 60511,
 60516,
 60519,
 60520,
 60521,
 60522,
 60523,
 60524,
 60525,
 60526,
 60527,
 60528,
 60529,
 60530,
 60602,
 60607,
 60611,
 60614,
 60615,
 60622,
 60627,
 60629,
 60632,
 60636,
 60638,
 60640,
 60644,
 60652,
 60654,
 60657,
 60658,
 60663,
 60664,
 60665,
 60666,
 60668,
 60669,
 60612,
 60661,
 60645,
 60629,
 60641,
 60654,
 60630,
 60670,
 60633,
 60676,
 60677,
 65000,
 65001,
 60517,
 60678,
 60909)
SCFactoryMeetMenuIndexes = (1903,
 1904,
 1906,
 1907,
 1908,
 1910,
 1913,
 1915,
 1916,
 1917,
 1919,
 1922,
 1923,
 1924,
 1932,
 1940,
 1941)
SCMenuCommonCogIndices = (20000, 20004)
SCMenuCustomCogIndices = {'bf': (20005, 20014),
 'nc': (20015, 20024),
 'ym': (20025, 20035),
 'ms': (20036, 20046),
 'bc': (20047, 20057),
 'cc': (20058, 20070),
 'nd': (20071, 20080),
 'ac': (20081, 20092),
 'tf': (20093, 20103),
 'hh': (20104, 20114),
 'le': (20115, 20124),
 'bs': (20125, 20135),
 'cr': (20136, 20145),
 'tbc': (20146, 20156),
 'ds': (20157, 20164),
 'gh': (20165, 20177),
 'pp': (20178, 20187),
 'b': (20188, 20199),
 'f': (20200, 20210),
 'mm': (20211, 20224),
 'tw': (20225, 20235),
 'mb': (20236, 20245),
 'm': (20246, 20254),
 'mh': (20255, 20266),
 'dt': (20267, 20276),
 'p': (20277, 20287),
 'tm': (20288, 20298),
 'bw': (20299, 20308),
 'ls': (20309, 20319),
 'rb': (20320, 20329),
 'sc': (20330, 20331),
 'sd': (20341, 20350)}
PSCMenuExpressions = 'EXPRESSIONS'
PSCMenuGreetings = 'GREETINGS'
PSCMenuGoodbyes = 'GOODBYES'
PSCMenuFriendly = 'FRIENDLY'
PSCMenuHappy = 'HAPPY'
PSCMenuSad = 'SAD'
PSCMenuSorry = 'SORRY'
PSCMenuCombat = 'COMBAT'
PSCMenuSeaCombat = 'SEA COMBAT'
PSCMenuPlaces = 'PLACES'
PSCMenuLetsSail = "LET'S SAIL..."
PSCMenuLetsHeadTo = "LET'S HEAD TO..."
PSCMenuHeadToPortRoyal = 'PORT ROYAL'
PSCMenuWhereIs = 'WHERE IS ..?'
PSCMenuWhereIsPortRoyal = 'PORT ROYAL'
PSCMenuWhereIsTortuga = 'TORTUGA'
PSCMenuWhereIsPadresDelFuego = 'PADRES DEL FUEGO'
PSCMenuWhereIsLasPulgas = 'LAS PULGAS'
PSCMenuWhereIsLosPadres = 'LOS PADRES'
PSCMenuDirections = 'DIRECTIONS'
PSCMenuInsults = 'INSULTS'
PSCMenuCompliments = 'COMPLIMENTS'
PSCMenuCardGames = 'CARD GAMES'
PSCMenuPoker = 'POKER'
PSCMenuBlackjack = 'BLACKJACK'
PSCMenuMinigames = 'MINIGAMES'
PSCMenuFishing = 'FISHING'
PSCMenuCannonDefense = 'CANNON DEFENSE'
PSCMenuPotions = 'POTION BREWING'
PSCMenuRepair = 'REPAIR'
PSCMenuInvitations = 'INVITATIONS'
PSCMenuVersusPlayer = 'VERSUS'
PSCMenuHunting = 'HUNTING'
PSCMenuQuests = 'QUESTS'
PSCMenuGM = 'GM'
PSCMenuShips = 'SHIPS'
PSCMenuAdventures = 'ADVENTURE'
GWSCMenuHello = 'GREETINGS'
GWSCMenuBye = 'GOODBYES'
GWSCMenuHappy = 'HAPPY'
GWSCMenuSad = 'SAD'
GWSCMenuPlaces = 'PLACES'
RandomButton = 'Randomize'
TypeANameButton = 'Type Name'
PickANameButton = 'Pick-A-Name'
NameShopSubmitButton = 'Submit'
RejectNameText = 'That name is not allowed. Please try again.'
WaitingForNameSubmission = 'Submitting your name...'
NameShopNameMaster = 'NameMasterEnglish.txt'
NameShopPay = 'Subscribe'
NameShopPlay = 'Free Trial'
NameShopOnlyPaid = 'Only paid users\nmay name their Toons.\nUntil you subscribe\nyour name will be\n'
NameShopContinueSubmission = 'Enter Toontown'
NameShopChooseAnother = 'Choose Another Name'
NameShopToonCouncil = 'The Toon Council\nhas approved your\nname!'
PleaseTypeName = 'Please type your name:'
ToonAlreadyExists = '%s already exists'
AllNewNames = 'All new names\nmust be approved\nby the Name Council.'
NameShopNameRejected = 'The name you\nsubmitted has\nbeen rejected.'
NameShopNameAccepted = 'Congratulations!\nThe name you\nsubmitted has\nbeen accepted!'
NoPunctuation = "You can't use punctuation marks in your name!"
PeriodOnlyAfterLetter = 'You can use a period in your name, but only after a letter.'
ApostropheOnlyAfterLetter = 'You can use an apostrophe in your name, but only after a letter.'
NoNumbersInTheMiddle = 'Numeric digits may not appear in the middle of a word.'
ThreeWordsOrLess = 'Your name must be three words or fewer.'
CopyrightedNames = ('mickey',
 'mickey mouse',
 'mickeymouse',
 'minnie',
 'minnie mouse',
 'minniemouse',
 'donald',
 'donald duck',
 'donaldduck',
 'pluto',
 'goofy')
NCTooShort = 'That name is too short.'
NCNoDigits = 'Your name cannot contain numbers.'
NCNeedLetters = 'Each word in your name must contain some letters.'
NCNeedVowels = 'Each word in your name must contain some vowels.'
NCAllCaps = 'Your name cannot be all capital letters.'
NCMixedCase = 'That name has too many capital letters.'
NCBadCharacter = "Your name cannot contain the character '%s'"
NCRepeatedChar = "Your name has too many of the character '%s'"
NCGeneric = 'Sorry, that name will not work.'
NCTooManyWords = 'Your name cannot be more than four words long.'
NCDashUsage = "Dashes may only be used to connect two words together (like in 'Boo-Boo')."
NCCommaEdge = 'Your name may not begin or end with a comma.'
NCCommaAfterWord = 'You may not begin a word with a comma.'
NCCommaUsage = 'That name does not use commas properly. Commas must join two words together, like in the name "Dr. Quack, MD". Commas must also be followed by a space.'
NCPeriodUsage = 'That name does not use periods properly. Periods are only allowed in words like "Mr.", "Mrs.", "J.T.", etc.'
NCApostrophes = 'That name has too many apostrophes.'
AvatarDetailPanelOK = lOK
AvatarDetailPanelCancel = lCancel
AvatarDetailPanelClose = lClose
AvatarDetailPanelLookup = 'Looking up details for %s.'
AvatarDetailPanelFailedLookup = 'Unable to get details for %s.'
AvatarDetailPanelPlayer = 'Player: %(player)s\nWorld: %(world)s\nLocation: %(location)s'
AvatarDetailPanelOnline = 'District: %(district)s\nLocation: %(location)s'
AvatarDetailPanelOffline = 'District: offline\nLocation: offline\nGuild: offline'
AvatarPanelFriends = 'Friends'
AvatarPanelWhisper = 'Whisper'
AvatarPanelSecrets = 'True Friends'
AvatarPanelGoTo = 'Go To'
AvatarPanelIgnore = 'Ignore'
AvatarPanelStopIgnore = 'Stop Ignoring'
AvatarPanelEndIgnore = 'End Ignore'
AvatarPanelTrade = 'Trade'
AvatarPanelCogLevel = 'Level: %s'
AvatarPanelCogDetailClose = lClose
TeleportPanelOK = lOK
TeleportPanelCancel = lCancel
TeleportPanelYes = lYes
TeleportPanelNo = lNo
TeleportPanelCheckAvailability = 'Trying to go to %s.'
TeleportPanelNotAvailable = '%s is busy right now; try again later.'
TeleportPanelIgnored = '%s is ignoring you.'
TeleportPanelNotOnline = "%s isn't online right now."
TeleportPanelWentAway = '%s went away.'
TeleportPanelUnknownHood = "You don't know how to get to %s!"
TeleportPanelUnavailableHood = '%s is not available right now; try again later.'
TeleportPanelDenySelf = "You can't go to yourself!"
TeleportPanelOtherShard = "%(avName)s is in district %(shardName)s, and you're in district %(myShardName)s.  Do you want to switch to %(shardName)s?"
KartRacingMenuSections = [-1,
 'PLACES',
 'RACES',
 'TRACKS',
 'COMPLIMENTS',
 'TAUNTS']
AprilToonsMenuSections = [-1,
 'GREETINGS',
 'PLAYGROUNDS',
 'CHARACTERS',
 'ESTATES']
SillyHolidayMenuSections = [-1, 'WORLD', 'BATTLE']
CarolMenuSections = [-1]
VictoryPartiesMenuSections = [-1, 'PARTY', 'ITEMS']
GolfMenuSections = [-1,
 'COURSES',
 'TIPS',
 'COMMENTS']
BoardingMenuSections = ['GROUP',
 "Let's go to...",
 "We're going to...",
 -1]
SellbotNerfMenuSections = [-1, 'GROUPING', 'SELLBOT TOWERS/VP']
JellybeanJamMenuSections = ['GET JELLYBEANS', 'SPEND JELLYBEANS']
WinterMenuSections = ['CAROLING', -1]
HalloweenMenuSections = [-1]
SingingMenuSections = [-1]
WhiteListMenu = [-1, 'WHITELIST']
SellbotInvasionMenuSections = [-1]
SellbotFieldOfficeMenuSections = [-1, 'STRATEGY']
IdesOfMarchMenuSections = [-1]
TTAccountCallCustomerService = 'Please call Customer Service at %s.'
TTAccountCustomerServiceHelp = '\nIf you need help, please call Customer Service at %s.'
TTAccountIntractibleError = 'An error occurred.'

InjectorTitle = 'Injector'
InjectorInject = 'Inject'
InjectorSave = 'Save'
InjectorLoad = 'Load'
InjectorRemove = 'Remove'
InjectorOops = 'Oops!'
InjectorOhYea = 'Oh yea!'
InjectorSaveQuestion = 'What do you want to name this code snippet?'
InjectorNotSaved = 'Your code snippet was not saved!'
InjectorSnippetExists = 'That snippet already exists. Do you want to replace it with this new one?'
InjectorSaved = 'Your code snippet was saved under "%s"!'
InjectorLoadQuestion = 'Which code snippet would you like to load?'
InjectorOverwriteWarning = 'This will overwrite your current code. Would you like to continue?'
InjectorLoaded = '"%s" was loaded successfully!'
InjectorRemoveQuestion = 'Which code snippet would you like to remove?'
InjectorRemoveWarning = 'This will remove the snippet "%s"! Are you sure you want to do this?'
InjectorRemoved = '"%s" was removed successfully!'

def timeElapsedString(timeDelta):
    timeDelta = abs(timeDelta)
    if timeDelta.days > 0:
        if timeDelta.days == 1:
            return '1 day ago'
        else:
            return '%s days ago' % timeDelta.days
    elif timeDelta.seconds / 3600 > 0:
        if timeDelta.seconds / 3600 == 1:
            return '1 hour ago'
        else:
            return '%s hours ago' % (timeDelta.seconds / 3600)
    elif timeDelta.seconds / 60 < 2:
        return '1 minute ago'
    else:
        return '%s minutes ago' % (timeDelta.seconds / 60)