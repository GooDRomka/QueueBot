import telebot
# from telebot import apihelper
# apihelper.proxy = {'https':'socks5://userproxy:password@proxy_address:port'}
import numpy as np

from Options import bot,Number,queue,Shops,choose_shop,Users,myQueue,Chat_shops,Chat_clients,flag,type_user,user_login
from Controller import send_text_controller,start_message_controller,help_message_controller

@bot.message_handler(commands=['help'])
def help_message(message):
    help_message_controller(message)


@bot.message_handler(commands=['start'])
def start_message(message):
    start_message_controller(message)

@bot.message_handler(content_types='text')
def send_text(message):
    send_text_controller(message)

bot.polling()
