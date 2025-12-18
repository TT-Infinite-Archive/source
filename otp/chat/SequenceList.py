from otp.settings import Settings

class SequenceList:
    def __init__(self, filePath):
        self.list = Settings.Settings(filePath)

        for key in list(self.list.keys()):
            sequences = self.list[key]
            if ',' in key:
                words = key.split(',')
                for word in words:
                    if word in self.list:
                        self.list[word].extend(sequences)
                    else:
                        self.list[word] = sequences


    def getList(self, word):
        if word in self.list:
            return self.list[word]
        else:
            return []
