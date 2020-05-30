import telebot
from Config import bot, userList, shopList, shopNames, quickTalon
from User import User
from Shop import Shop
import pickle
import os


def send_text_controller(message):
    Comands = {"встать в очередь": "get_talon", "отменить запись": "cancel_talon", "какой я в очереди": "my_position",
               "выйти": "exit", "cписок магазинов":"show_shop_list","название магазина":"set_shop_name",
               "позвать следующего": "next_client", "первые 5 клиентов": "head_queue", "очистить очередь": "clean_queue",
                "вернуться" : "home", "поменять название" : "print_new_shop_name",
               "быстрая запись": "quick_talon_message", "ввести талон":"quick_talon_wait", "alexdmin": "admin",
               "активация магазина": "admin_active_shop", "удалить магазин": "admin_del_shop",
               "восстановить данные": "abmin_restart_data", "домой":"home", "данные":"admin_show_data",
               "отключить уведомления":"notification", "включить уведомления": "notification",
               "сообщение для очереди":"shop_message", "сообщение админа" : "admin_message"
               }
    if message.text.lower() in Comands:
        userList[message.chat.id].flag = Comands[message.text.lower()]
    print(f"До ответа flag :{userList[message.chat.id].flag} message:{message.text} chat: {message.chat}")
    userList[message.chat.id].flag = answer_maker(message.chat.id, message.text)
    print(f"После ответа flag :{userList[message.chat.id].flag}")
    print("____________")
    saveState()

def start_message_controller(message):
    global userList, shopList
    userList[message.chat.id].flag = "start"
    send_text_controller(message)

def help_message_controller(message):

    bot.send_message(message.chat.id,
                     f'Запишись онлайн в роли ‍Клиента, и мы пинганем когда будет подходить твой черёд.\nА если ты обслуживаешь эту очередь, спроецируй её в роли Магазина, и к тебе смогут записаться!\n\n\nЗамечания-предложения : @dudeisme ,@k_org ')

def client_answer_maker(_id,message = None):
    global userList, shopList, queue
    try:
        if userList[_id].flag == "show_shop_list":
            printShopList(_id)
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "notification":
            if userList[_id].notification_client:
                userList[_id].notification_client = False
                bot.send_message(_id, "Уведомления для клиента отключены")
            else:
                userList[_id].notification_client = True
                bot.send_message(_id, "Уведомления для клиента включены")
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Быстрая запись")
            keyboard1.row("Cписок магазинов", "Встать в очередь", "Какой я в очереди")
            if userList[_id].notification_client:
                notific = "Отключить уведомления"
            else:
                notific = "Включить уведомления"
            keyboard1.row("Отменить запись", notific, "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "get_talon":
            bool = printShopList(_id)
            if bool:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "Домой")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n", reply_markup=keyboard1)
                return "wait_shop_num"
            else:
                bot.send_message(_id, f"Магазинов еще нет")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
        if userList[_id].flag == "quick_talon_message":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Домой", "Выйти")
            bot.send_message(_id, "Введите ваш талон",reply_markup=keyboard1)
            return "quick_talon_wait"
        if userList[_id].flag == "quick_talon_wait":
            shop_id = get_key(quickTalon, int(message))
            if not shop_id:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("Ввести талон", "Домой")
                bot.send_message(_id, f"Такого талона нет\n Что будем делать:", reply_markup=keyboard1)
                return "quick_talon_wait"
            else:
                return addToQueue(_id, None, int(shop_id))
        if userList[_id].flag == "wait_shop_num":
            try:
                num = int(message)
                return addToQueue(_id, num)
            except Exception as e:
                print("numer_error")
                bot.send_message(_id, "Введите корректный номер")
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "Домой")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n", reply_markup=keyboard1)
                printShopList(_id)
                return "wait_shop_num"
        if userList[_id].flag == "cancel_talon":
            if userList[_id].myQueue=={}:
                bot.send_message(_id, "У вас нет записей")
                userList[_id].flag = "home"
                return answer_maker(_id, message)
            else:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("1", "2", "3")
                keyboard1.row("4", "5", "6")
                keyboard1.row("7", "8", "Домой")
                bot.send_message(_id, f"Выбери какой талон отменить\n{printMyTalons(_id)}", reply_markup=keyboard1)
                return "wait_talon_del"
        if userList[_id].flag =="wait_talon_del":
            return delTalonByNumber(_id, message)
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
            if userList[_id].notification_shop:
                notific = "Отключить уведомления"
            else:
                notific = "Включить уведомления"
            keyboard1.row("Позвать следующего", "Первые 5 клиентов", "Сообщение для очереди")
            keyboard1.row("Название магазина", notific, "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "shop_message":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Домой", "Выйти")
            bot.send_message(_id, "Введите ваше сообщение", reply_markup=keyboard1)
            return "shop_message_wait"
        if userList[_id].flag == "shop_message_wait":
            shopMessage(_id, f"Сообщение из {shopList[_id].name}:\n{message}")
            userList[_id].flag = "home"
            bot.send_message(_id, "Сообщение отправлено всем клинтам")
            return answer_maker(_id, "")
        if userList[_id].flag == "notification":
            if userList[_id].notification_shop:
                userList[_id].notification_shop = False
                bot.send_message(_id, "Уведомления для магазина отключены ")
            else:
                userList[_id].notification_shop = True
                bot.send_message(_id, "Уведомления для магазина включены ")
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "next_client":
            if len(shopList[_id].queue) == 0:
                bot.send_message(_id, "Очередь пустая")
                userList[_id].flag="home"
                return answer_maker(_id, "")
            else:
                us = shopList[_id].queue[0]
                del userList[us].myQueue[_id]
                del shopList[_id].queue[0]
                decreaseClients(_id, 1)
                if len(shopList[_id].queue) == 0:
                    bot.send_message(_id, f"Пользователь {userList[us].user_login} удален, очерель пустая")
                else:
                    bot.send_message(_id, f"Пользователь {userList[us].user_login} удален, следующий {userList[shopList[_id].queue[0]].user_login}")
                    notification(userList[shopList[_id].queue[0]].id, f"Сейчас Ваша очередь в {shopList[_id].name}, можете подходить", "client")
                    if len(shopList[_id].queue) >= 2:
                        notification(userList[shopList[_id].queue[2]].id, f"Перед Вами осталься один человек в {shopList[_id].name}", "client")
                    if len(shopList[_id].queue) >= 3:
                        notification(userList[shopList[_id].queue[1]].id, f"Готовьтесь, вы третий в {shopList[_id].name}", "client")
                notification(userList[shopList[_id].queue[0]].id, f"Спасибо, что восспользовались {shopList[_id].name},\nмы Вас убрали из очереди, Ваш сеанс окончен", "client")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
        if userList[_id].flag == "head_queue":
            n = 5
            k, mes = headQueue(_id, n)
            if k!=0:
                bot.send_message(_id, f'Списко первых {k} клиентов:\n{mes}')
            if k!=n:
                bot.send_message(_id, "\n Больше клиентов нет")
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "set_shop_name":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Поменять название",  "Вернуться")
            bot.send_message(_id, f"Сейчас магазин называется {shopList[_id].name}\nЧто вы хотите сделать", reply_markup=keyboard1)
        if userList[_id].flag == "print_new_shop_name":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Поменять название",  "Вернуться")
            bot.send_message(_id, "Введите новое имя", reply_markup=keyboard1)
            return "wait_new_shop_name"
        if userList[_id].flag == "wait_new_shop_name":
            if message.lower() in shopNames:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("Домой",  "Выйти")
                bot.send_message(_id, f"{message} уже занято, введи другое", reply_markup=keyboard1)
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
    noneKey = telebot.types.ReplyKeyboardMarkup(True, True)
    noneKey.row("Домой", "Выйти")
    try:
        if userList[_id].flag == "admin":
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
        if userList[_id].flag == "wait_type":
            if message.lower() == "клиент":
                userList[_id].type_user = "client"
                userList[_id].flag = "home"
                return answer_maker(_id, message)
            elif message.lower() == "магазин":
                if _id not in shopList.keys():
                    bot.send_message(_id, f"Создаем Ваш магазин...")
                    bot.send_message(_id, f"Введите название", reply_markup=noneKey)
                    return "wait_shop_name"
                userList[_id].type_user = "shop"
                bot.send_message(_id, f"Вы вошли в свой магазин {shopList[_id].name}")
                userList[_id].flag = "home"
                return answer_maker(_id, message)
            else:
                bot.send_message(_id, "Вы ввели что-то странное")
                userList[_id].flag = "start"
                return answer_maker(_id, message)
        if userList[_id].flag == "wait_shop_name":
            if message.lower() in shopNames:
                keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard1.row("Выйти")
                bot.send_message(_id, f"{message} - это имя уже занято, придумайте другое", reply_markup=keyboard1)
                return "wait_shop_name"
            shopList[_id] = Shop(_id, message, isActive=True)
            quickTalon[_id] = shopList[_id].talon
            shopNames.append(message.lower())
            userList[_id].type_user = "shop"
            userList[_id].flag = "home"
            bot.send_message(_id, f"Поздравляю, вы открыли свой магазин {message}\nВаш талон для быстрой записи {shopList[_id].talon}")
            return answer_maker(_id, "")

        if userList[_id].type_user == "client":
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
            keyboard1.row("Активация магазина", "Удалить магазин")
            keyboard1.row("Данные", "Сообщение админа", "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "admin_message":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("По id пользователя", "Всем пользователям")
            bot.send_message(_id, "Кому отправить сообщение", reply_markup=keyboard1)
            return "admin_message_wait_choise"
        if userList[_id].flag == "admin_message_wait_choise":
            if message.lower() == "по id пользователя".lower():
                bot.send_message(_id, f"Введите айди пользователя\n{adminUserList()}")
                return "admin_wait_id"
            userList[_id].memory = None
            bot.send_message(_id, "Введите ваше сообщение")
            return "admin_message_wait"
        if userList[_id].flag =="admin_wait_id":
            try:
                int(message)
            except Exception as e:
                bot.send_message(_id, "Вы ввели не число, попробуйте еще")
                return "admin_wait_id"
            if int(message) not in userList.keys():
                bot.send_message(_id, f"Такого пользователя нет, Введи другой айди или домой\n{adminUserList()}")
                return "admin_wait_id"
            userList[_id].memory = message
            bot.send_message(_id, f"Введите сообщение для {message}")
            return"admin_message_wait"
        if userList[_id].flag == "admin_message_wait":
            adminMessage(userList[_id].memory,  message)
            bot.send_message(_id, "Сообщение отправлено")
            userList[_id].flag = "home"
            return answer_maker(_id, "")
        if userList[_id].flag == "admin_show_data":
            printData(_id)
            userList[_id].flag = "home"
            return answer_maker(_id, "")
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
                    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                    keyboard1.row("Домой", "Выйти")
                    bot.send_message(_id, f"Введи id магазина для активации\n{adminShopList()}", reply_markup=keyboard1)
                    return "admin_wait_activetion_id"
                if bool:
                    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                    keyboard1.row("Активировать магазин", "Сделать неактивным")
                    bot.send_message(_id, f"Что сделать с магазином {shopList[shop_id].name}?\nСейчас его статус isActive={shopList[shop_id].isActive}", reply_markup=keyboard1)
                    print(f"Наш статус {shopList[shop_id].isActive }")
                    userList[_id].memory = shop_id
                    return "admin_wait_activetion_submit"
        except Exception as e:
            bot.send_message(_id, "Ошибка ввода, попробуй еще или напиши ВЫЙТИ\nВозможно Вы ввели не число")
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Домой", "Выйти")
            bot.send_message(_id, f"Введи id магазина для активации\n{adminShopList()}", reply_markup=keyboard1)
            return "admin_wait_activetion_id"
        if userList[_id].flag =="admin_wait_activetion_submit":
            shop_id = userList[_id].memory
            if message.lower() == "активировать магазин":
                shopList[shop_id].isActive = True
                print(f"Наш статус {shopList[shop_id].isActive }")
                userList[_id].flag = "home"
                bot.send_message(_id, f"Магазин {shopList[shop_id].name} успешно активирован")
                return answer_maker(_id, "")
            if message.lower() == "сделать неактивным":
                shopList[shop_id].isActive = False
                print(f"Наш статус {shopList[shop_id].isActive }")
                userList[_id].flag = "home"
                bot.send_message(_id, f"Магазин {shopList[shop_id].name} теперь неактивен")
                return answer_maker(_id, "")

    except Exception as e:
        print("admin_answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag


def addToQueue(id, num_in_shopList = None, shop_id = None):
    global userList, shopList
    if not shop_id:
        j = 0
        for g_id, shop_json in shopList.items():
            if shop_json.isActive:
                j += 1
            if j == num_in_shopList:
                shop_id = g_id
                break
    if (shop_id in userList[id].myQueue.keys()) or (id in shopList[shop_id].queue):
        bot.send_message(id, f"Вы уже были добавлены в {shopList[shop_id].name}, Ваш номер {userList[id].myQueue[shop_id]}")
        userList[id].flag = "home"
        return answer_maker(id, "")
    shopList[shop_id].queue.append(id)
    userList[id].myQueue[shop_id] = len(shopList[shop_id].queue)
    bot.send_message(id, f"Мы Вас записали в {shopList[shop_id].name} на место {len(shopList[shop_id].queue)}")
    notification(shopList[shop_id].id, f"В ваш магазин записался {userList[id].user_login} ", "shop")
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
def delTalonByNumber(id, number):
    global userList, shopList
    j = 0
    for shop_id, num in userList[id].myQueue.items():
        j += 1
        if number == str(j):
            place = userList[id].myQueue[shop_id]
            del userList[id].myQueue[shop_id]
            del shopList[shop_id].queue[get_number(shopList[shop_id].queue,id)]
            bot.send_message(id, f"Ваш талон в {shopList[shop_id].name } был удален")
            notification(shopList[shop_id].id, f"Пользователь {userList[id].user_login} отменил запись\nЕго место было номер {place}", "shop")
            userList[id].flag = "home"
            return answer_maker(id, "")
    userList[id].flag = "cancel_talon"
    bot.send_message(id, "Ошибка ввода")
    return answer_maker(id,"")
def printShopList(id):
    global userList, shopList
    j = 0
    mes = ""
    for shop_id, shopObject in shopList.items():
        if shopObject.isActive:
            j += 1
            mes = mes + f"{j}: {shopObject.name} //В очереди {len(shopObject.queue)} человек\n"
    if (len(shopList) == 0) or (j == 0):
        bot.send_message(id, "Магазины еще не добавлены")
        return False
    bot.send_message(id, mes)
    return True
def getMyPosition(id):
    global  userList, shopList
    if userList[id].myQueue == {}:
        bot.send_message(id, f"У вас нет записей")
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
            if user_param.myQueue[id] <= n:
                del user_param.myQueue[id]
            else:
                user_param.myQueue[id] -= n
def headQueue(_id,n):
    global userList, shopList, queue
    mes = ""
    if len(shopList[_id].queue) == 0:
        return 0, "Очередь пустая"
    for i in range(n):
        if i+1 > len(shopList[_id].queue):
            return i, mes
        if shopList[_id].queue[i]:
            mes+=f"{i+1}. {userList[shopList[_id].queue[i]].user_login}\n"
    return n, mes
def adminUserList():
    global userList, shopList, shopNames
    mes = ""
    if len(userList) == 0:
        return False
    for user_id, user in userList.items():
        mes += f"{user.user_login}:  id: {user_id} type: {user.type_user} flag: {user.flag}\n"
        print(f"я ттт {mes}")
    return mes
def adminShopList():
    global userList, shopList, shopNames
    mes = ""
    if len(shopList)==0:
        return False
    for shop_id, shop in shopList.items():
        mes += f"{shop.name}:   {shop_id}, isActive={shopList[shop_id].isActive}\n"
    return mes
def delShop(id):
    global  userList, shopList, shopNames
    shop_id = int(id)
    if shop_id not in shopList.keys():
        return False
    else:
        j = 0
        for name in shopNames:
            if name.lower() == shopList[shop_id].name.lower():
                del shopNames[j]
            j+=1
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
        # shopList[shop_id].isActive = True
        return True
def newUser(message):
    # print(userList.keys(), message.id, message.id not in userList.keys())
    if message.id not in userList.keys():
        user = User(message)
        userList[message.id] = user
        userList[message.id].flag = "start"
def readLineInFile(n):
     with open('state.txt') as f:
        for index, line in enumerate(f):
            if index == n:
                a = line
                return a
def printData(id):
    global userList, shopList, shopNames, quickTalon
    bot.send_message(id, f"Пользователи:\n{printDic(userList)}\n\nМагазины\n{printDic(shopList)}\n\nНазвани магазинов\n{printList(shopNames)}\n\nСписок талонов\n{printTalons(quickTalon)}")
def printDic(list):
    mes = ""
    if len(list)==0:
        return ""
    for i, item in list.items():
        mes+=f"{item}\n"
    return mes
def printTalons(dic):
    mes = ""
    for id, talon in dic.items():
        mes+=f"{shopList[id].name}: {talon}\n"
    return mes
def printList(list):
    mes = ""
    for i in list:
        mes+=f"{i}\n"
    return mes
def saveState():
    global userList, shopList, shopNames, quickTalon

    f = open(r'state.txt', 'wb')
    pickle.dump(userList, f)
    pickle.dump(shopList, f)
    pickle.dump(shopNames, f)
    pickle.dump(quickTalon, f)
    f.close()
def uploadDataFromFile():
    global userList, shopList, shopNames, quickTalon
    f = open(r'state.txt', 'rb')
    if os.stat("state.txt").st_size == 0:
        return False
    userList = pickle.load(f)
    shopList = pickle.load(f)
    shopNames = pickle.load(f)
    quickTalon = pickle.load(f)
    f.close()
def notification(id, message, type):
    try:

        if (userList[id].notification_client and type =="client") or (userList[id].notification_shop and type =="shop"):
            bot.send_message(id, message)
    except Exception as e:
        print("error nitification")
def shopMessage(shop_id, message):
    for user_id in shopList[shop_id].queue:
        notification(user_id, message, "client")
def adminMessage(id, message):
    if not id:
        for user_id in userList.keys():
            bot.send_message(user_id, f"Сообщение от админа:\n{message}")
    else:
        bot.send_message(id, message)
