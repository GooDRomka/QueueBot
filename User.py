
class User:
    def __init__(self, message):
        self.id = message.id
        self.flag = 'start'
        self.user_login = message.username
        self.type_user = ''
        self.myQueue = {}
