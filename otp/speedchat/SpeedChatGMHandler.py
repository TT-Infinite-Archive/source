from panda3d.core import ConfigVariableInt, ConfigVariableString
from direct.showbase import DirectObject
from otp.otpbase import OTPLocalizer


class SpeedChatGMHandler(DirectObject.DirectObject):
    scStructure = None
    scList = {}

    def __init__(self):
        if SpeedChatGMHandler.scStructure is None:
            self.generateSCStructure()

    def generateSCStructure(self):
        SpeedChatGMHandler.scStructure = [OTPLocalizer.PSCMenuGM]
        phraseCount = 0
        numGMCategories = ConfigVariableInt('num-gm-categories', 0).getValue()
        for i in range(0, numGMCategories):
            categoryName = ConfigVariableString(f'gm-category-{i}', '').getValue()
            if categoryName == '':
                continue
            categoryStructure = [categoryName]
            numCategoryPhrases = ConfigVariableInt(f'gm-category-{i}-phrases', 0).getValue()
            for j in range(0, numCategoryPhrases):
                phrase = ConfigVariableString(f'gm-category-{i}-phrase-{j}', '').getValue()
                if phrase != '':
                    idx = f'gm{phraseCount}'
                    SpeedChatGMHandler.scList[idx] = phrase
                    categoryStructure.append(idx)
                    phraseCount += 1

            SpeedChatGMHandler.scStructure.append(categoryStructure)

        numGMPhrases = ConfigVariableInt('num-gm-phrases', 0).getValue()
        for i in range(0, numGMPhrases):
            phrase = ConfigVariableString(f'gm-phrase-{i}', '').getValue()
            if phrase != '':
                idx = f'gm{phraseCount}'
                SpeedChatGMHandler.scList[idx] = phrase
                SpeedChatGMHandler.scStructure.append(idx)
                phraseCount += 1

    def getStructure(self):
        return SpeedChatGMHandler.scStructure

    def getPhrase(self, id):
        return SpeedChatGMHandler.scList[id]
