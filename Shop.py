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

        print(f"\n\n\nДобавлен новый магазин id: {self.id} name:{self.name}\n\n\n")
    def _asdict(self):
        return self.__dict__
    def __repr__(self):
        return "Shop id:% s name:% s talon:% s isActive:% s queue:% s " % (self.id, self.name, self.talon, self.isActive, self.queue)


    id = ""
    name = ""
    queue = []
