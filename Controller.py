import telebot
from QueueBot.Config import Carma, max_number_clients, bot, Number, queue, Shops, choose_shop, Users, myQueue, Chat_shops, Chat_clients, flag, type_user, user_login


def send_text_controller(message):
    User_name = "мой друг"
    global flag
    Comands = {"стать в очередь": "get_talon", "отменить запись": "cancel_talon", "какой я в очереди": "my_position",
               "выйти": "exit","cписок магазинов":"show_shop_list",
               "позвать следующего": "next_client", "первые 3 клиента": "head_queue", "очистить очередь": "clean_queue",
               "удалить магазин": "delete_shop"
               }
    if message.text.lower() in Comands:
        flag = Comands[message.text.lower()]
    print(f"До ответа flag :{flag} message:{message.text} Users: {Users} Shops:{Shops} queue:{queue} myQueue:{myQueue}")
    flag = answer_maker(message.chat.id, message.text.lower())

    print(f"После ответа flag :{flag} message:{message.text}  Users: {Users} Shops:{Shops} queue:{queue} myQueue:{myQueue}")


def start_message_controller(message):
    global flag, type_user, user_login, Users, Shops
    flag = "start"
    send_text_controller(message)

def help_message_controller(message):
    bot.send_message(message.chat.id,
                     f'Привет, напиши: \n/start чтобы авторизироваться\n/help чтобы узнать список компанд \n"Пока" для выхода')


def answer_maker(_id, message=None):
    global flag, type_user, user_login, Users, Shops,queue,myQueue
    try:
        if flag == "start":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard1.row("Клиент", "Магазин")
            bot.send_message(_id, "Выбери свою роль", reply_markup=keyboard1)
            return "wait_type"
        if flag == "exit":
            type_user = ""
            flag = "start"
            return answer_maker(_id,"")
        if flag == "wait_type":
            if message == "клиент":
                Users.append(_id)
                type_user = "client"
                myQueue[_id] = {}
                flag = "home"

                return answer_maker(_id, message)
            elif message == "магазин":
                Shops.append(_id)
                queue[_id] = {}
                type_user = "shop"
                flag = "home"
                return answer_maker(_id, message)
            else:
                bot.send_message(_id, "Неверный ввод")
                flag = "start"
                return answer_maker(_id, message)
        if flag == "show_shop_list":
            printShopList(_id)
            flag = "home"
            return answer_maker(_id,"")
        if flag == "home":
            keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
            if type_user == "client":
                keyboard1.row("Cписок магазинов","Стать в очередь", "Отменить запись", "Какой я в очереди", "Выйти")
                bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            elif type_user == "shop":
                keyboard1.row("Позвать следующего", "Первые 3 клиента", "Очистить очередь", "Удалить магазин", "Выйти")
                bot.send_message(_id, "Выбери действие", reply_markup=keyboard1)
            else:
                flag = "start"
                return answer_maker(_id, message)
        if flag == "get_talon":
            bot.send_message(_id, "Выбери магазин в котором встать в очередь\n")
            printShopList(_id)
            return "wait_shop_num"
        if flag == "wait_shop_num":
            try:
                num = int(message)
                return addToQueue(_id, num - 1)
            except Exception as e:
                print("numer_error")
                bot.send_message(_id, "Введите корректный номер")
                bot.send_message(_id, "Выбери магазин в котором встать в очередь\n")
                printShopList(_id)
                return "wait_shop_num"
        if flag == "cancel_talon":
            if myQueue[_id]=={}:
                bot.send_message(_id, "У вас нет записей")
                flag = "home"
                return answer_maker(_id,message)
            else:
                bot.send_message(_id,f"Выбери какой талон отменить\n{printMyTalons(_id)}")
                return "wait_talon_del"
        if flag =="wait_talon_del":
            return delTalonByNumber(_id,message)
        if flag == "my_position":
            return getMyPosition(_id)

    except Exception as e:
        print("answer_maker_error")
        bot.send_message(_id, "Попробуй выполнить команду еще раз")
        return flag


def addToQueue(id, num_in_shops):
    global flag, type_user, user_login, Users, Shops, queue, myQueue
    if Shops[num_in_shops] in myQueue[id]:
        bot.send_message(id,f"Вы уже были добавлены в {Shops[num_in_shops]}, Ваш номер {myQueue[id][Shops[num_in_shops]]}")
        flag = "home"
        return answer_maker(id,"")
    queue[Shops[num_in_shops]].append(id)
    myQueue[id][Shops[num_in_shops]] = len(queue[Shops[num_in_shops]])
    bot.send_message(id, f"Мы Вас записали в {Shops[num_in_shops]} на место {len(queue[Shops[num_in_shops]])}")
    flag = "home"
    return answer_maker(id, "")

def printMyTalons(id):
    global flag, type_user, user_login, Users, Shops, queue,myQueue
    mes = ""
    j = 0
    for shop, num in myQueue[id].items():
        j += 1
        mes+=f"{j}: {shop} номер в очереди {num}\n"
    return mes
def delTalonByNumber(id,number):
    global flag, type_user, user_login, Users, Shops, queue,myQueue
    j = 0
    for shop, num in myQueue[id].items():
        j+=1
        if number == str(j):
            del myQueue[id][shop]
            del queue[shop][queue[shop].index(id)]
            bot.send_message(id, f"Ваш тало в {shop} был удален")
            print(f"я тут 2")
            flag = "home"
            return answer_maker(id,"")
    flag = "cancel_talon"
    bot.send_message(id,"Ошибка ввода")
    return answer_maker(id,"")
def printShopList(id):
    global flag, type_user, user_login, Users, Shops, queue, myQueue
    j = 0
    mes = ""
    for i in Shops:
        j += 1
        mes = mes + f"{j}: {i}\n"
    print(f"mes:{mes}")
    bot.send_message(id, mes)
def getMyPosition(id):
    global flag, type_user, user_login, Users, Shops, queue, myQueue
    if myQueue[id] == {}:
        bot.send_message(id,f"У вас нет записей")
        flag = "home"
        return answer_maker(id, "")
    else:
        mes = ""
        for shop,num in myQueue[id].items():
            mes+= f"В магазине {shop} Ваша очередь {num}\n"
        bot.send_message(id,mes)
        flag = "home"
        return answer_maker(id,"")
def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
