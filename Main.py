from QueueBot.Config import bot
from QueueBot.Controller import (
    send_text_controller,
    start_message_controller,
    help_message_controller,
)


@bot.message_handler(commands=["help"])
def help_message(message):
    help_message_controller(message)


@bot.message_handler(commands=["start"])
def start_message(message):
    start_message_controller(message)


@bot.message_handler(content_types="text")
def send_text(message):
    send_text_controller(message)


bot.polling()
