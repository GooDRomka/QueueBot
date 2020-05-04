import telebot
from QueueBot.Config import bot, userList, shopList,shopNames, quickTalon
from QueueBot.User import User
from QueueBot.Shop import Shop
import simplejson

def send_text_controller(message):
    Comands = {"встать в очередь": "get_talon", "отменить запись": "cancel_talon", "какой я в очереди": "my_position",
               "выйти": "exit", "cписок магазинов":"show_shop_list","изменить название магазина":"set_shop_name",
               "позвать следующего": "next_client", "первые 3 клиента": "head_queue", "очистить очередь": "clean_queue",
                "вернуться" : "home", "поменять название" : "print_new_shop_name",
               "быстрая запись": "quick_talon_message", "ввести талон":"quick_talon_wait", "admin": "admin",
               "активировать магазин": "admin_active_shop", "удалить магазин": "admin_del_shop",
               "восстановить данные": "abmin_restart_data"
               }
    print(message)
    if message.text.lower() in Comands:
        userList[message.chat.id].flag = Comands[message.text.lower()]
    print(f"До ответа flag :{userList[message.chat.id].flag} message:{message.text} userList: {userList} shopList:{shopList}  myQueue:{userList[message.chat.id].myQueue}")
    userList[message.chat.id].flag = answer_maker(message.chat.id, message.text)
    print(f"После ответа flag :{userList[message.chat.id].flag} message:{message.text}  userList: {userList} shopList:{shopList}  myQueue:{userList[message.chat.id].myQueue}")
    saveState()

def start_message_controller(message):
    global userList, shopList
    user = User(message.from_user)
    userList[message.chat.id] = user
    userList[message.chat.id].flag = "start"
    send_text_controller(message)

def help_message_controller(message):
    bot.send_message(message.chat.id,
                     f'Привет, напиши: \n/start чтобы авторизироваться\n/help чтобы узнать список компанд ')

def client_answer_maker(_id,message = None):
    global userList, shopList, queue
    try:
        if userList[_id].flag == "show_shop_list":
            printShopList(_id)
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Cписок магазинов", "Встать в очередь", "Какой я в очереди")
            keyboard1.row("Отменить запись", "Быстрая запись","Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "get_talon":
            bool = printShopList(_id)
            if bool:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "9")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n", reply_markup=keyboard1)
                return "wait_shop_num"
            else:
                userList[_id].flag = "home"
                return answer_maker(_id, "")
        if userList[_id].flag == "quick_talon_message":
            bot.send_message(_id, "Введите ваш талон")
            return "quick_talon_wait"
        if userList[_id].flag == "quick_talon_wait":
            shop_id = get_key(quickTalon, int(message))
            print(f"Я тут 0 {shop_id} {quickTalon}")
            if not shop_id:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("Ввести талон", "Выйти")
                bot.send_message(_id, f"Такого талона нет\n Что будем делать:", reply_markup=keyboard1)
                return "quick_talon_wait"
            else:
                return addToQueue(_id, "", int(shop_id))

        if userList[_id].flag == "wait_shop_num":
            try:
                num = int(message)
                return addToQueue(_id, num - 1)
            except Exception as e:
                print("numer_error")
                bot.send_message(_id, "Введите корректный номер")
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "9")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n", reply_markup=keyboard1)
                printShopList(_id)
                return "wait_shop_num"
        if userList[_id].flag == "cancel_talon":
            if userList[_id].myQueue=={}:
                bot.send_message(_id, "У вас нет записей")
                userList[_id].flag = "home"
                return answer_maker(_id,message)
            else:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "9")
                bot.send_message(_id, f"Выбери какой талон отменить\n{printMyTalons(_id)}", reply_markup=keyboard1)
                return "wait_talon_del"
        if userList[_id].flag =="wait_talon_del":
            return delTalonByNumber(_id,message)
        if userList[_id].flag == "my_position":
            return getMyPosition(_id)
    except Exception as e:
        print("user_answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag

def shop_answer_maker(_id, message = None):
    global userList, shopList, shopNames
    try:
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Позвать следующего", "Первые 3 клиента")
            keyboard1.row("Изменить название магазина", "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "next_client":
            if len(shopList[_id].queue) == 0:
                bot.send_message(_id, "Очередь пустая")
                userList[_id].flag="home"
                return answer_maker(_id, "")
            else:
                print(f"я тут 0")
                us = shopList[_id].queue[0]
                del userList[us].myQueue[_id]
                del shopList[_id].queue[0]
                print(f"я тут 1")
                decreaseClients(_id, 1)
                print(f"я тут 2")
                if len(shopList[_id].queue) == 0:
                    bot.send_message(_id, f"Пользователь {us} удален, очерель пустая")
                else:
                    bot.send_message(_id, f"Пользователь {us} удален, следующий {shopList[_id].queue[0]}")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
        if userList[_id].flag == "head_queue":
            n = 3
            k, mes = headQueue(_id,n)
            if k!=0:
                bot.send_message(_id,f'Списко первых {k} клиентов:\n{mes}')
            if k!= n:
                bot.send_message(_id,"\n Больше клиентов нет")
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "set_shop_name":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Поменять название",  "Вернуться")
            bot.send_message(_id, f"Сейчас магазин называется {shopList[_id].name}\nЧто вы хотите сделать",reply_markup=keyboard1)
        if userList[_id].flag == "print_new_shop_name":
            bot.send_message(_id, "Введите новое имя")
            return "wait_new_shop_name"
        if userList[_id].flag == "wait_new_shop_name":
            if message.lower() in shopNames:
                bot.send_message(_id, f"{message} уже занято, введи другое")
                return "wait_new_shop_name"
            else:
                shopNames.append(message.lower())
                shopList[_id].name = message
                bot.send_message(_id, f"Ваш магазин теперь называется {message}")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
    except Exception as e:
        print("shop_answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag

def answer_maker(_id, message=None):
    global userList, shopList
    try:
        if userList[_id].flag == "admin":
            if _id not in userList.keys():
                    userList.append(_id)
                    userList[_id].myQueue = {}
            userList[_id].type_user = "admin"
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "start":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Клиент", "Магазин")
            bot.send_message(_id, "Выбери свою роль", reply_markup=keyboard1)
            return "wait_type"
        if userList[_id].flag == "exit":
            userList[_id].type_user = ""
            userList[_id].flag = "start"
            return answer_maker(_id, "")
        if userList[_id].flag == "wait_shop_name":
            shopList[_id] = Shop(_id, message, isActive=True)
            userList[_id].type_user = "shop"
            userList[_id].flag = "home"
            quickTalon[_id] = shopList[_id].talon
            bot.send_message(_id, f"Поздравляю, вы открыли свой магазин {message}\nВаш талон для быстрой записи {shopList[_id].talon}")
            return answer_maker(_id, "")
        if userList[_id].flag == "wait_type":
            if message.lower() == "клиент":
                if _id not in userList.keys():
                    userList.append(_id)
                    userList[_id].myQueue = {}
                userList[_id].type_user = "client"
                userList[_id].flag = "home"
                return answer_maker(_id, message)
            elif message.lower() == "магазин":
                if _id not in shopList.keys():
                    bot.send_message(_id, f"Создаем Ваш магазин...")
                    bot.send_message(_id, f"Введите название")
                    return "wait_shop_name"
                userList[_id].type_user = "shop"
                bot.send_message(_id,f"Вы вошли в свой магазин {shopList[_id].name}")
                userList[_id].flag = "home"
                return answer_maker(_id, message)
            else:
                bot.send_message(_id, "Неверный ввод")
                userList[_id].flag = "start"
                return answer_maker(_id, message)
        if userList[_id].type_user=="client":
            return client_answer_maker(_id,message)
        elif userList[_id].type_user=="shop":
            return shop_answer_maker(_id,message)
        elif userList[_id].type_user=="admin":
            return admin_answer_maker(_id, message)
        else:
            userList[_id].flag = "start"
            return answer_maker(_id, message)
    except Exception as e:
        print("answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag

def admin_answer_maker(_id, message=None):
    global userList, shopList, shopNames
    try:
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Активировать магазин", "Удалить магазин")
            keyboard1.row("Восстановить данные", "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "admin_del_shop":
            mes = adminShopList()
            if not mes:
                bot.send_message(_id, "Нечего удалять")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
            bot.send_message(_id, f"Введи id магазина для удаления\n{mes}")
            return "admin_wait_del_id"
        try:
            if userList[_id].flag == "admin_wait_del_id":
                bool = delShop(message)
                if not bool:
                    bot.send_message(_id, "Такого магазина нет")
                    bot.send_message(_id, f"Введи id магазина для удаления или можно ВЫЙТИ\n{adminShopList()}")
                    return "admin_wait_del_id"
                if bool:
                    bot.send_message(_id, f"Магазин {message} успешно удален")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
        except Exception as e:
            bot.send_message(_id, "Ошибка ввода, попробуй еще или напиши ВЫЙТИ\nВозможно Вы ввели не число")
            bot.send_message(_id, f"Введи id магазина для удаления\n{adminShopList()}")
            return "admin_wait_del_id"

        if userList[_id].flag =="admin_active_shop":
            mes = adminShopList()
            if not mes:
                bot.send_message(_id, "Список магазинов пуст")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
            bot.send_message(_id, f"Введи id магазина для активации\n{mes}")
            return "admin_wait_activetion_id"
        try:
            if userList[_id].flag == "admin_wait_activetion_id":
                bool = activeShop(message)
                shop_id = int(message)
                if not bool:
                    bot.send_message(_id, "Такого магазина нет")
                    bot.send_message(_id, f"Введи id магазина для активации или можно ВЫЙТИ\n{adminShopList()}")
                    return "admin_wait_activetion_id"
                if bool:
                    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                    keyboard1.row("Активировать магазин", "Сделать неактивным")
                    bot.send_message(_id, f"Что сделать с магазином {shopList[shop_id].name}?\nСейчас его статус isActive={shopList[shop_id].isActive}", reply_markup=keyboard1)
                    userList[_id].memory = shop_id
                    return "admin_wait_activetion_submit"
        except Exception as e:
            bot.send_message(_id, "Ошибка ввода, попробуй еще или напиши ВЫЙТИ\nВозможно Вы ввели не число")
            bot.send_message(_id, f"Введи id магазина для активации\n{adminShopList()}")
            return "admin_wait_activetion_id"
        if userList[_id].flag =="admin_wait_activetion_submit":
            shop_id = userList[_id].memory
            if message.lower()=="активировать магазин":
                shopList[shop_id].isActive = True
                userList[_id].flag = "home"
                bot.send_message(_id, f"Магазин {shopList[shop_id].name} успешно активирован")
                return answer_maker(_id, "")
            if message.lower() == "сделать неактивным":
                shopList[shop_id].isActive = False
                userList[_id].flag = "home"
                bot.send_message(_id, f"Магазин {shopList[shop_id].name} теперь неактивен")

                return answer_maker(_id, "")

    except Exception as e:
        print("admin_answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag



def addToQueue(id, num_in_shopList = None, shop_id = None):
    global userList, shopList
    print(f"я тут 0 {num_in_shopList}")
    if not shop_id:
        j = 0
        print(f"я тут 1 {num_in_shopList}")
        for g_id, shop_json in shopList.items():
            if shop_json.isActive:
                print(f"я тут 2 {j}")
                j += 1
            if j - 1 == num_in_shopList:
                print(f"я тут 3 {j} {g_id}")
                shop_id = g_id


    if shop_id in userList[id].myQueue.keys():
        bot.send_message(id, f"Вы уже были добавлены в {shopList[shop_id].name}, Ваш номер {userList[id].myQueue[shop_id]}")
        userList[id].flag = "home"
        return answer_maker(id, "")
    shopList[shop_id].queue.append(id)
    userList[id].myQueue[shop_id] = len(shopList[shop_id].queue)
    bot.send_message(id, f"Мы Вас записали в {shopList[shop_id].name} на место {len(shopList[shop_id].queue)}")
    userList[id].flag = "home"
    return answer_maker(id, "")

def printMyTalons(id):
    global  userList, shopList
    mes = ""
    j = 0
    for shop, num in userList[id].myQueue.items():
        j += 1
        mes+=f"{j}: {shopList[shop].name} номер в очереди {num}\n"
    return mes

def delTalonByNumber(id,number):
    global userList, shopList
    j = 0
    for shop_id, num in userList[id].myQueue.items():
        j += 1
        if number == str(j):
            del userList[id].myQueue[shop_id]
            del shopList[shop_id].queue[get_number(shopList[shop_id].queue,id)]
            bot.send_message(id, f"Ваш талон в {shopList[shop_id].name } был удален")
            userList[id].flag = "home"
            return answer_maker(id,"")
    userList[id].flag = "cancel_talon"
    bot.send_message(id,"Ошибка ввода")
    return answer_maker(id,"")

def printShopList(id):
    global userList, shopList
    j = 0
    mes = ""
    for shop_id, shopObject in shopList.items():
        print(f"я сломался 1 {shopObject}")
        if shopObject.isActive:
            j += 1
            mes = mes + f"{j}: {shopObject.name}\n"
    print(f"я сломался 1 {j}")
    print(f"mes:{mes}")
    if (len(shopList) == 0) or (j == 0):
        bot.send_message(id, "Магазины еще не добавлены")
        return False
    bot.send_message(id, mes)
    return True
def getMyPosition(id):
    global  userList, shopList
    if userList[id].myQueue == {}:
        bot.send_message(id,f"У вас нет записей")
        userList[id].flag = "home"
        return answer_maker(id, "")
    else:
        mes = ""
        for shop_id, num in userList[id].myQueue.items():
            mes+= f"В магазине {shopList[shop_id].name} Ваша очередь {num}\n"
        bot.send_message(id, mes)
        userList[id].flag = "home"
        return answer_maker(id,"")

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
    return False
def get_number(m, value):
    j = 0
    for i in m:
        if i == value:
            return j
        j += 1

def decreaseClients(id, n):
    for us_id, user_param in userList.items():
        if id in user_param.myQueue.keys():
            user_param.myQueue[id]-=n

def saveState():
    global userList, shopList, shopNames
    f = open('state.txt', 'w')
    mes = "import telebot\n#bot = telebot.TeleBot('1086481184:AAE0h7NBROzRO7Ke2QmTd7qPOYGy3WTMCM0')\nbot = telebot.TeleBot('1234407671:AAEKcRhsafPOVfIwNRLP1oU69rJ8xly6ZtE')\n"
    mes = mes + f"shopList = {simplejson.dumps(shopList)}\nuserList = {simplejson.dumps(userList)}\nshopNames ={shopNames}\nquickTalon = {quickTalon}"
    f.write(mes.replace('true', 'True').replace('false', 'False').replace('null', 'None'))
    f.close()
def headQueue(_id,n):
    global  userList, shopList, queue
    mes = ""
    if len(shopList[_id].queue)==0:
        return 0, "Очередь пустая"

    for i in range(n):
        if i>=len(shopList[_id].queue):
            return i, mes
        if shopList[_id].queue[i]:
            mes+=f"{i+1}. {userList[shopList[_id].queue[i]].user_login}\n"
    return n, mes
def adminShopList():
    global  userList, shopList, shopNames
    mes = ""
    if len(shopList)==0:
        return False
    for shop_id, shop in shopList.items():
        mes += f"{shop.name}: {shop_id}"
    return mes
def delShop(id):
    global  userList, shopList, shopNames
    shop_id = int(id)
    if shop_id not in shopList.keys():
        return False
    else:
        for name in shopNames:
            if name == shopList[shop_id].name.lower():
                del name
        del shopList[shop_id]
        del quickTalon[shop_id]
        for us_id, user in userList.items():
            if shop_id in user.myQueue.keys():
                del user.myQueue[shop_id]
        return True

def activeShop(id):
    global userList, shopList, shopNames
    shop_id = int(id)
    if shop_id not in shopList.keys():
        return False
    else:
        shopList[shop_id].isActive = True
        return True

def newUser(message):
    if message.id not in userList.keys():
        print(f"Добавлен новый пользлователь {message.id}")
        user = User(message)
        userList[message.id] = user
        userList[message.id].flag = "start"

# def uploadDataFromFile():
