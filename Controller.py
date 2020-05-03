import telebot
from QueueBot.Config import  bot, userList, shopList,shopNames
from QueueBot.User import User
from QueueBot.Shop import Shop
import simplejson

def send_text_controller(message):
    Comands = {"встать в очередь": "get_talon", "отменить запись": "cancel_talon", "какой я в очереди": "my_position",
               "выйти": "exit","cписок магазинов":"show_shop_list","изменить имя магазина":"set_shop_name",
               "позвать следующего": "next_client", "первые 3 клиента": "head_queue", "очистить очередь": "clean_queue",
               "удалить магазин": "delete_shop", "вернуться" : "home", "поменять название" : "print_new_shop_name"
               }

    if message.text.lower() in Comands:
        userList[message.chat.id].flag = Comands[message.text.lower()]
    print(f"До ответа flag :{userList[message.chat.id].flag} message:{message.text} userList: {userList} shopList:{shopList}  myQueue:{userList[message.chat.id].myQueue}")
    userList[message.chat.id].flag = answer_maker(message.chat.id, message.text)
    print(f"После ответа flag :{userList[message.chat.id].flag} message:{message.text}  userList: {userList} shopList:{shopList}  myQueue:{userList[message.chat.id].myQueue}")
    saveState()

def start_message_controller(message):
    global  userList, shopList
    user = User(message.from_user)
    userList[message.chat.id] = user
    userList[message.chat.id].flag = "start"
    send_text_controller(message)

def help_message_controller(message):
    bot.send_message(message.chat.id,
                     f'Привет, напиши: \n/start чтобы авторизироваться\n/help чтобы узнать список компанд ')

def client_answer_maker(_id,message = None):
    global  userList, shopList, queue
    try:
        if userList[_id].flag == "show_shop_list":
            printShopList(_id)
            userList[_id].flag = "home"
            return answer_maker(_id,"")
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Cписок магазинов","Встать в очередь", "Отменить запись", "Какой я в очереди", "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "get_talon":
            bot.send_message(_id, "Выбери магазин в котором встать в очередь\n")
            printShopList(_id)
            return "wait_shop_num"
        if userList[_id].flag == "wait_shop_num":
            try:
                num = int(message)
                return addToQueue(_id, num - 1)
            except Exception as e:
                print("numer_error")
                bot.send_message(_id, "Введите корректный номер")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n")
                printShopList(_id)
                return "wait_shop_num"
        if userList[_id].flag == "cancel_talon":
            if userList[_id].myQueue=={}:
                bot.send_message(_id, "У вас нет записей")
                userList[_id].flag = "home"
                return answer_maker(_id,message)
            else:
                bot.send_message(_id,f"Выбери какой талон отменить\n{printMyTalons(_id)}")
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
    global  userList, shopList, shopNames
    try:
        if userList[_id].flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Позвать следующего", "Первые 3 клиента", "Изменить имя магазина", "Выйти")
            bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            return "wait_choise"
        if userList[_id].flag == "next_client":
            if len(shopList[_id].queue) == 0:
                bot.send_message(_id,"Очередь пустая")
                userList[_id].flag="home"
                return answer_maker(_id,"")
            else:
                print(f"я тут 0")
                us = shopList[_id].queue[0]
                del userList[us].myQueue[_id]
                del shopList[_id].queue[0]
                print(f"я тут 1")
                decreaseClients(_id,1)
                print(f"я тут 2")
                if len(shopList[_id].queue) == 0:
                    bot.send_message(_id,f"Пользователь {us} удален, очерель пустая")
                else:
                    bot.send_message(_id,f"Пользователь {us} удален, следующий {shopList[_id].queue[0]}")
                userList[_id].flag = "home"
                return answer_maker(_id,"")
        if userList[_id].flag == "head_queue":
            n = 3
            k, mes = headQueue(_id,n)
            if k!=0:
                bot.send_message(_id,f'Списко первых {k} клиентов:\n{mes}')
            if k!= n:
                bot.send_message(_id,"\n Больше клиентов нет")
            userList[_id].flag = "home"
            return answer_maker(_id,"")
        if userList[_id].flag == "set_shop_name":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Поменять название",  "Вернуться")
            bot.send_message(_id,f"Сейчас магазин называется {shopList[_id].name}\nЧто вы хотите сделать",reply_markup=keyboard1)
        if userList[_id].flag == "print_new_shop_name":
            bot.send_message(_id,"Введите новое имя")
            return "wait_new_shop_name"
        if userList[_id].flag == "wait_new_shop_name":
            if message.lower() in shopNames:
                bot.send_message(_id,f"{message} уже занято, введи другое")
                return "wait_new_shop_name"
            else:
                shopNames.append(message.lower())
                shopList[_id].name = message
                bot.send_message(_id,f"Ваш магазин теперь называется {message}")
                userList[_id].flag = "home"
                return answer_maker(_id, "")
    except Exception as e:
        print("shop_answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag

def answer_maker(_id, message=None):
    global  userList, shopList
    try:
        if userList[_id].flag == "start":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Клиент", "Магазин")
            bot.send_message(_id, "Выбери свою роль", reply_markup=keyboard1)
            return "wait_type"
        if userList[_id].flag == "exit":
            userList[_id].type_user = ""
            userList[_id].flag = "start"
            return answer_maker(_id,"")
        if userList[_id].flag == "wait_shop_name":
            shopList[_id] = Shop(_id, message)
            userList[_id].type_user = "shop"
            userList[_id].flag = "home"
            bot.send_message(_id, f"Поздравляю, вы открыли свой магазин {message}")
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
                    bot.send_message(_id,f"Создаем Ваш магазин...")
                    bot.send_message(_id,f"Введите название")
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
        else:
            userList[_id].flag = "start"
            return answer_maker(_id, message)
    except Exception as e:
        print("answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return userList[_id].flag


def addToQueue(id, num_in_shopList):
    global userList, shopList
    j=0
    shop_id = ""
    for _id, shop_json in shopList.items():
        if j == num_in_shopList:
            shop_id = _id
        j += 1
    if shop_id in userList[id].myQueue.keys():
        bot.send_message(id,f"Вы уже были добавлены в {shopList[shop_id].name}, Ваш номер {userList[id].myQueue[shop_id]}")
        userList[id].flag = "home"
        return answer_maker(id,"")
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
    global  userList, shopList
    j = 0
    for shop_id, num in userList[id].myQueue.items():
        j+=1
        if number == str(j):
            del userList[id].myQueue[shop_id]
            del shopList[shop_id].queue[get_number(shopList[shop_id].queue,id)]
            bot.send_message(id, f"Ваш тало в {shopList[shop_id].name } был удален")
            userList[id].flag = "home"
            return answer_maker(id,"")
    userList[id].flag = "cancel_talon"
    bot.send_message(id,"Ошибка ввода")
    return answer_maker(id,"")
def printShopList(id):
    global  userList, shopList
    j = 0
    mes = ""
    for shop_id, shopObject in shopList.items():
        j += 1
        mes = mes + f"{j}: {shopList[shop_id].name}\n"
    print(f"mes:{mes}")
    bot.send_message(id, mes)
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
def get_number(m, value):
    j=0
    for i in m:
        if i == value:
            return j
        j+=1
def decreaseClients(id,n):
    for us_id, user_param in userList.items():
        if id in user_param.myQueue.keys():
            user_param.myQueue[id]-=n
def saveState():
    global  userList, shopList, shopNames
    f = open('state.txt', 'w')
    mes = f"\n\n\nshopList = {simplejson.dumps(shopList)}\nuserList = {simplejson.dumps(userList)}\nshopNames ={shopNames}\n"
    f.write(mes)
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
            mes+=f"{i}. {userList[shopList[_id].queue[i]].user_login}\n"
    return n, mes
