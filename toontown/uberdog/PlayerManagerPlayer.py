class PlayerManagerPlayer:
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.avId = data.get('avId', 0)
        self.name = data.get('name', '')
        self.laff = data.get('laff', 0)

    def toList(self):
        return [self.avId, self.name, self.laff]

    def fromList(self, ls):
        self.avId = ls[0]
        self.name = ls[1]
        self.laff = ls[2]