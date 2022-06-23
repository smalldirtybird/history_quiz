import logging
import os
import random
import traceback
from dotenv import load_dotenv

from question_files_operations import convert_quiz_files_to_dict
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text='Привет, я бот для викторин!',
                     reply_markup=reply_markup)


def echo(bot, update):
    if update.message.text == 'Новый вопрос':
        question_number = random_id=random.randint(1, len(quiz_questions))
        update.message.reply_text(quiz_questions[question_number]['question'])
    else:
        update.message.reply_text(update.message.text)


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"', update, traceback.format_exc())


if __name__ == '__main__':
    logging.basicConfig(
        filename='tg_bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
        )
    load_dotenv()
    quiz_questions = convert_quiz_files_to_dict('/home/drew/Documents/GitHub/history_quiz/quiz_questions/')
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

