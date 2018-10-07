class PeriodicList(list):
    def __getitem__(self, index):
        return super().__getitem__(index % len(self))
