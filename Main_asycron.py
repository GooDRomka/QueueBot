# -*- coding: utf-8 -*-
import telegram
from telebot import TeleBot
import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import PeriodicCallback, IOLoop
from asyncio import Queue
# периодический запуск синхронных задач по обработке задач в очереди запросов
class CustomPeriodicCallback(PeriodicCallback):
    def __init__(self, request_queue, response_queue, callback_time, io_loop=None):
        if callback_time <= 0:
            raise ValueError("Periodic callback must have a positive callback_time")
        self.callback_time = callback_time
        self.io_loop = io_loop or IOLoop.current()
        self._running = False
        self._timeout = None
        self.request_queue = request_queue
        self.response_queue = response_queue

    # обработка очереди, однопоточная работа с базой данных
    # взяли из очереди задачу, обработали, записали результат и сказали что задача выполенена
    def queue_callback(self):
        try:
            message = self.request_queue.get_nowait()
        except Exception as QueueEmpty:
            pass
        else:
            start = False
            is_reset = False
            if message['text'] == 'telegram_cmd':
                self.response_queue.put({
                    'chat_id':message['chat_id'],
                    'wait_message_id':message['wait_message_id'],
                    'message_text': question,
                    'markup': markup
                })
            self.request_queue.task_done()

    def _run(self):
        if not self._running:
            return
        try:
            return self.queue_callback()
        except Exception:
            self.io_loop.handle_callback_exception(self.queue_callback)
        finally:
            self._schedule_next()

# периодический запуск получения запросов с серверов Telegram и отправка ответов
class BotPeriodicCallback(PeriodicCallback):
    def __init__(self, bot, callback_time, io_loop=None):
        if callback_time <= 0:
            raise ValueError("Periodic callback must have a positive callback_time")
        self.callback_time = callback_time
        self.io_loop = io_loop or IOLoop.current()
        self._running = False
        self._timeout = None
        self.bot = bot

    def bot_callback(self, timeout=1):
        #print 'bot_callback'
        if self.bot.skip_pending:
            self.bot.skip_pending = False
        updates = self.bot.get_updates(offset=(self.bot.last_update_id + 1), timeout=timeout)
        self.bot.process_new_updates(updates)
        self.bot.send_response_messages()

    def _run(self):
        if not self._running:
            return
        try:
            return self.bot_callback()
        except Exception:
            self.io_loop.handle_callback_exception(self.bot_callback)
        finally:
            self._schedule_next()

# Добавление к боту очередей запросов и результатов
class AppTeleBot(TeleBot, object):
    def __init__(self, token, request_queue, response_queue, threaded=True, skip_pending=False):
        super(AppTeleBot, self).__init__(token, threaded=True, skip_pending=False)
        self.request_queue = request_queue
        self.response_queue = response_queue

    # Отправка всех обработанных данных из очереди результатов
    def send_response_messages(self):
        try:
            message = self.response_queue.get_nowait()
        except QueueEmpty:
            pass
        else:
            self.send_chat_action(message['chat_id'], 'typing')
            if message['message_text'] == 'contact':
                self.send_contact(message['chat_id'], phone_number=PHONE_NUMBER, last_name=LAST_NAME, first_name=FIRST_NAME, reply_markup=message['markup'])
            else:
                self.send_message(message['chat_id'], message['message_text'], reply_markup=message['markup'])
            self.response_queue.task_done()

def main():
    TOKEN = 'telegram api token'

    request_queue = Queue(maxsize=0) # очередь запросов
    response_queue = Queue(maxsize=0) # очередь результатов
    bot = AppTeleBot(TOKEN, request_queue, response_queue)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        pass

    # добавление запросов к боту в очередь запросов
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def echo_all(message):
        markup = telegram.ReplyKeyboardRemove(selective=False)
        response = bot.send_message(message.chat.id,  u'Подождите...', reply_markup=markup)
        bot.request_queue.put({
            'text': message.text,
            'chat_id': message.chat.id,
            'username': message.chat.username,
            'first_name': message.chat.first_name,
            'last_name': message.chat.last_name,
            'message_id': message.message_id,
            'wait_message_id': response.message_id
        })


    ioloop = tornado.ioloop.IOLoop.instance()

    BotPeriodicCallback(bot, 1000, ioloop).start()
    CustomPeriodicCallback(request_queue, response_queue, 1000, ioloop).start()

    ioloop.start()


if __name__ == "__main__":
    main()
