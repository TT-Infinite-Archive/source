class PlayerManagerPlayer:
    def __init__(self, data):
        self.name = data.get('name', '')
        self.species = data.get('species', '')
        self.laff = data.get('laff', 0)
        self.access = data.get('access', 0)

    def toList(self):
        return [self.name, self.species, self.laff, self.access]