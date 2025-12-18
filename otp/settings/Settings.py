import collections
import json
import os


class Settings(collections.abc.MutableMapping):
    def __init__(self, path):
        self.path = path

        self.store = {}
        self.read()

    def read(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.store = json.load(f)
            except:
                # Looks like our preferences got corrupted. Let's write a new one for the user.
                # TODO: Find out why this even happens ~ Chan.
                self.write()
        else:
            self.write()

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self.store, f, sort_keys=True, indent=2, separators=(',', ': '))

    def __setitem__(self, key, value):
        self.store[key] = value
        self.write()

    def __delitem__(self, key):
        del self.store[key]
        self.write()

    def __getitem__(self, key):
        return self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
