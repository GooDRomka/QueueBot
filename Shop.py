class Shop:
    def __init__(self, id, name):
        self.id = id
        # self.holder = message.chat.id
        self.name = name
        self.queue = []

    def _asdict(self):
        return self.__dict__


    id = ""
    name = ""
    queue = []
