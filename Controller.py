import telebot
from Options import Carma,max_number_clients,bot,Number,queue,Shops,choose_shop,Users,myQueue,Chat_shops,Chat_clients,flag,type_user,user_login

def send_text_controller(message):
    User_name = "мой друг"
    global flag
    print(f'Флаг в начале отправки {flag}')
    Comands = {'привет':"start",'пока':"finish", "клиент":'client','магазин':'shop',
               "войти в аккаунт":"login","cоздать новый":"","какой я в очереди":"my_position",
               "выбрать магазин":"choice_shop","отменить запись":"cancel_record","выйти": "finish"
            }
    if message.text.lower() in Comands:
        flag = Comands[message.text.lower()]
    flag = answer_maker(User_name, message.chat.id, message.text)
    if flag == "work":
        answer_maker(User_name, message.chat.id, message.text)
    print(f"флаг после {flag} \n {Users} {Shops} {queue}")

def start_message_controller(message):
    global flag,type_user,user_login,Users,Shops
    _id = message.chat.id
    bot.send_message(message.chat.id, f'Привет, напиши \n /start чтобы начать\n /help чтобы узнать список компанд')
    User_name = ""
    flag = "start"
    _id = message.chat.id
    if not User_name:
        User_name = "мой друг"
    answer_maker(User_name, message.chat.id, message = message)

def help_message_controller(message):
    bot.send_message(message.chat.id, f'Привет, напиши: \n/start чтобы авторизироваться\n/help чтобы узнать список компанд \n"Пока" для выхода \n/slavaUkraine')

def answer_maker( User_name, _id, message=None):
    try:
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
        global flag,type_user,user_login,Users,Shops,Chat_shops,Chat_clients,queue,choose_shop,Carma
        print(f'Флаг в начале {flag}')
        if flag == "work":
             keyboard1.row("Выбрать магазин", "Отменить запись", "Какой я в очереди", "Выйти")
             bot.send_message(_id, "Что хотите сделать дальше", reply_markup=keyboard1)
        if flag=="start":
            keyboard1.row("Клиент", "Магазин")
            bot.send_message(_id, "Выбери свою роль",reply_markup=keyboard1)
            return "wait_type"
        if flag=="finish":
            bot.send_message(_id, f'Прощай, {User_name}')
            bot.send_message(_id, f'напиши /start чтобы начать')
            user_login =""
            type_user = ""
            return "start"
        if flag == 'client' or flag=='shop':
            keyboard1.row("Войти в аккаунт", "Создать новый")
            bot.send_message(_id, f"Вы выбрали {flag}")
            type_user = flag
            bot.send_message(_id, "Что хотите сделать дальше", reply_markup=keyboard1)
            return "wait_type_aut"
        if flag == "wait_type_aut":
            if message=="Войти в аккаунт":
                flag='login'
            elif message=="Создать новый":
                flag="create_acc"
            else:
                flag = type_user
        if flag=="create_acc":
            bot.send_message(_id, 'Придумай логин')
            return "wait_login_reg"
        if flag == 'wait_login_reg':
            return new_acc(_id,message)
        if flag == "wait_password":
            if type_user=="client":
                Users[user_login] = message
                myQueue[user_login]={}
                Carma[user_login] = 10
                Chat_clients[user_login]=_id
            else:
                Shops[user_login] = message
                queue[user_login] = {}
                Chat_shops[user_login]=_id
            bot.send_message(_id, 'Принято, теперь можно работать')
            return "work"
        if flag=="login":
            bot.send_message(_id, 'Введите Ваш логин')
            return "wait_login_aut"
        if flag=="wait_login_aut":
            user_login = message
            if user_login not in Users:
                bot.send_message(_id, 'Введите Ваш настоящий логин')
                return "wait_login_aut"
            bot.send_message(_id, 'Введите Ваш пароль')
            return "wait_password_log"
        if flag =="wait_password_log":
            return login(_id, message)
        if flag == "my_position":
            if user_login not in myQueue:
                bot.send_message(_id,"Вы еще никуда не записались")
            else:
                bot.send_message(_id,f"Ваши записи:\n {myQueue[user_login]} ")
            return "work"
        if flag == "cancel_record":

            if (user_login not in myQueue) or (len(myQueue[user_login].keys())) == 0:
                bot.send_message(_id,"Вы еще никуда не записались")
            else:
                bot.send_message(_id, f"Из какого магазина Вас убрать: {myQueue[user_login].keys()}")
            return "wait_choice_cancel"
        if flag == "wait_choice_cancel":
            print(f"удаляю из {user_login}, {queue}, {queue[message]}")
            if get_key(queue[message],user_login):
                print("удаляю")
                del queue[message][get_key(queue[message],user_login)]
                del myQueue[user_login][message]
                bot.send_message(_id, f"Вы больше не записаны в {message} ")
            else:
                bot.send_message(_id, f"Вы больше не записаны в {message} ")
            return "work"
        if flag == "choice_shop":
            bot.send_message(_id, f"Ловите список магазинов, в какой записать Вас?: {[Shops.keys()]}")
            return "wait_choice_shop"
        if flag == "wait_choice_shop":
            if message in queue.keys():
                 if message in myQueue[user_login]:
                     bot.send_message(_id,f'Вы уже записаны в {message},\nВаша очередь там {myQueue[user_login][message]}')
                     return "work"
                 bot.send_message(_id,f'свободны такие номера{freeNum(message)}')
                 choose_shop = message
                 return "wait_number_queue"
            elif message not in Shops:
                bot.send_message(_id, f'Нет такого магазина')
                return "choice_shop"
            else:
                bot.send_message(_id,'Все номера свободный, введите на какой номер Вас записать')
                choose_shop = message
                return "wait_number_queue"
        if flag == "wait_number_queue":
            if not message.isdigit():
                bot.send_message(_id,"введите число больше 0")
            if int(message)<=0:
                bot.send_message(_id,"введите число больше 0")
            if choose_shop not in queue:
                queue[choose_shop] = {}
                queue[choose_shop][message] = user_login
                if user_login not in myQueue:
                    myQueue[user_login] = {}
                myQueue[user_login][choose_shop] = message
                bot.send_message(_id,f'Вы записаны в {choose_shop}, порядок в очереди {message}')
            elif message in queue[choose_shop].keys():
                bot.send_message(_id,f'Номер занят, посмотри еще\n {freeNum(choose_shop)}')
                return "wait_number_queue"
            else:
                queue[choose_shop][message] = user_login
                myQueue[user_login][choose_shop] = message
                bot.send_message(_id,f'Вы записаны в {choose_shop}, порядок в очереди {message}')
        return "work"
    except Exception as e:
        print("answer_maker_error")
        bot.send_message(_id,"Попробуй еще раз выполнить последнюю команду")


def new_acc(_id, login):
    global flag,Users,Shops,user_login
    if type_user == 'client':
        if login in Users:
            bot.send_message(_id, 'Ваш логин занят')
            flag = "create_acc"
        else:
            bot.send_message(_id, 'Принято, теперь придумай пароль')
            user_login = login
            flag = "wait_password"
    if type_user == 'shop':
        if login in Shops:
            bot.send_message(_id, 'Ваш логин занят')
            flag = "wait_login_reg"
        else:
            bot.send_message(_id, 'Принято, теперь придумай пароль')
            user_login = login
            flag = "wait_password"
    print(Users,flag)
    return flag
def login(_id,password):
    global type_user,user_login,Users,Shops
    if type_user=='client':
        if Users[user_login]==password:
            bot.send_message(_id, 'успешно вошли')
            return "work"
        else:
            bot.send_message(_id, 'попробуй еще')
            return "wait_password_log"
    if type_user=='shop':
        if Shops[user_login]==password:
            bot.send_message(_id, 'успешно вошли')
            return "work"
        else:
            bot.send_message(_id, 'попробуй еще')
            return "wait_password_log"
def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
def freeNum(choose_shop):
    global queue,max_number_clients
    res = []
    print(f'{queue[choose_shop].keys()}')
    return list([set(range(1,max_number_clients))-set([int(item) for item in queue[choose_shop].keys()])])
