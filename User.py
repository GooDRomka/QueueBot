
class User:
    def __init__(self, message):
        self.id = message.id
        self.flag = 'start'
        if message.first_name:
            self.user_login = message.first_name
        elif message.username:
            self.user_login = message.username
        elif message.last_name:
            self.user_login = message.last_name
        else:
             self.user_login = message.id
        self.user_login = message.username
        self.type_user = ''
        self.myQueue = {}
        self.memory = ""
        print(f"\n\nДобавлен новый пользлователь id: {self.id} name:{self.user_login}\n\n")
    def __repr__(self):
        return "User id:% s name:% s type:% s flag:% s queue:% s" % (self.id, self.user_login, self.type_user, self.flag, self.myQueue)
    def _asdict(self):
        return self.__dict__
    id = ""
    flag = ""
    user_login = ""
    type_user =""
    myQueue = {}
