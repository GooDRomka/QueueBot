
from Controller import send_text_controller, start_message_controller, help_message_controller, newUser, uploadDataFromFile
from Config import bot
import logging
import telebot
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

try:
    uploadDataFromFile()
    print("Данные восстановленны")
except Exception as e:
    print("Ошибка восстановления данных")
print("BOT STARTED")

@bot.message_handler(commands=["help"])
def help_message(message):
    newUser(message.from_user)
    help_message_controller(message)


@bot.message_handler(commands=["start"])
def start_message(message):
    newUser(message.from_user)
    try:
        start_message_controller(message)
    except Exception as e:
        message.text = "/start"
        print('ERROR in start_message')
        start_message_controller(message)


@bot.message_handler(content_types="text")
def send_text(message):
    newUser(message.from_user)
    try:
        send_text_controller(message)
    except Exception as e:
         print('ERROR in send_text')
         message.text = "/start"
         send_text_controller(message)

bot.polling(none_stop=True, interval=0)
