import telebot
import json

bot = telebot.TeleBot('1086481184:AAE0h7NBROzRO7Ke2QmTd7qPOYGy3WTMCM0')
Number = []
queue = {"Food": [],"Spa":[]}
Shops = ["Food","Spa"]

choose_shop = ""
Users = []
myQueue = {}
Carma = {}
Chat_shops = {}
Chat_clients = {}
flag = 'start'
type_user = ""
user_login = ""
max_number_clients = 10
