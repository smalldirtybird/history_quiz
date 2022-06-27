import logging
import os
import random
import traceback

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from question_files_operations import convert_quiz_files_to_dict


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text='Привет, я бот для викторин!',
                     reply_markup=reply_markup)


def echo(bot, update):
    if update.message.text == 'Новый вопрос':
        question_number = random.randint(1, len(quiz_questions))
        update.message.reply_text(quiz_questions[question_number]['questsion'])
    else:
        update.message.reply_text(update.message.text)


if __name__ == '__main__':
    logging.basicConfig(
        filename='tg_bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
        )
    load_dotenv()
    redis_connection = redis.Redis(host=os.environ['DB_HOST'], port=os.environ['DB_PORT'])
    print(redis_connection)
    quiz_questions = convert_quiz_files_to_dict('/home/drew/Documents/quiz_questions/')
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()
