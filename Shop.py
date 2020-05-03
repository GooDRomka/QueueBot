class Shop:
    def __init__(self, id, name, talon = None, isActive = False):
        self.id = id
        # self.holder = message.chat.id
        self.name = name
        self.queue = []
        if not talon:
            self.talon = id
        else:
            self.talon = talon
        self.isActive = isActive
    def _asdict(self):
        return self.__dict__


    id = ""
    name = ""
    queue = []
