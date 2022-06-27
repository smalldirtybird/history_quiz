import logging
import os
import random
import re

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from question_files_operations import convert_quiz_files_to_dict

WAITING, QUESTION_ASKED = range(2)


def start(bot, update):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text='Привет, я бот для викторин!',
                     reply_markup=reply_markup)
    return WAITING


def handle_new_question_request(bot, update):
    chat_id = update['message']['chat']['id']
    question_number = str(random.randint(1, len(quiz_questions)))
    quiz_question = quiz_questions[question_number]['question']
    redis_connection.set(chat_id, question_number)
    update.message.reply_text(quiz_question)
    print(quiz_questions[question_number]['answer'])
    return QUESTION_ASKED


def handle_solution_attempt(bot, update):
    chat_id = update['message']['chat']['id']
    question_number = redis_connection.get(chat_id).decode('UTF-8')
    correct_answer = quiz_questions[question_number]['answer']
    answer, explanation = re.split('\.| \(', correct_answer, maxsplit=1)
    print(answer)
    print(explanation)
    if update.message.text == answer:
        bot.send_message(chat_id=update['message']['chat']['id'],
                         text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»”')
        return WAITING
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return QUESTION_ASKED


def handle_retreat(bot, update):
    chat_id = update['message']['chat']['id']
    question_number = redis_connection.get(chat_id).decode('UTF-8')
    correct_answer = quiz_questions[question_number]['answer']
    answer, explanation = re.split('\.| \(', correct_answer, maxsplit=1)
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text=f'Правильный ответ:\n{answer}')
    new_question_number = str(random.randint(1, len(quiz_questions)))
    new_quiz_question = quiz_questions[new_question_number]['question']
    redis_connection.set(chat_id, new_question_number)
    update.message.reply_text(f'Новый вопрос:\n{new_quiz_question}')
    print(quiz_questions[new_question_number]['answer'])
    return QUESTION_ASKED


def done(bot, update):
    update.message.reply_text("Пока, до следующего раза!")
    return ConversationHandler.END


if __name__ == '__main__':
    logging.basicConfig(
        filename='tg_bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
        )
    load_dotenv()
    redis_connection = redis.Redis(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        password=os.environ['DB_PASSWORD']
        )
    quiz_questions = convert_quiz_files_to_dict('/home/drew/Documents/quiz_questions/')
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING: [RegexHandler('^Новый вопрос$', handle_new_question_request)],
            QUESTION_ASKED: [RegexHandler('^Сдаться$', handle_retreat),
                             MessageHandler(Filters.text, handle_solution_attempt)
                             ]
            },
        fallbacks=[RegexHandler('^Done$', done)]
        )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
