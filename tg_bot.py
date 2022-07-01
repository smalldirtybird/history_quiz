import logging
import os
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler, Updater)

from quiz_question_operations import (convert_quiz_files_to_dict,
                                      get_question_content_from_database,
                                      save_new_question_content_to_database)

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
    save_new_question_content_to_database(
        chat_id, redis_connection, quiz_content)
    new_quiz_question = get_question_content_from_database(
        chat_id, redis_connection)['question']
    update.message.reply_text(new_quiz_question)
    return QUESTION_ASKED


def handle_solution_attempt(bot, update):
    chat_id = update['message']['chat']['id']
    correct_answer = get_question_content_from_database(
        chat_id, redis_connection)['answer']
    if update.message.text == correct_answer:
        bot.send_message(chat_id=update['message']['chat']['id'],
                         text=dedent(
                             '''
                             Правильно! Поздравляю!
                             Для следующего вопроса нажми «Новый вопрос»”
                             ''')
                         )
        return WAITING
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return QUESTION_ASKED


def handle_retreat(bot, update):
    chat_id = update['message']['chat']['id']
    correct_answer = get_question_content_from_database(
        chat_id, redis_connection)['answer']
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text=f'Правильный ответ:\n{correct_answer}')
    save_new_question_content_to_database(
        chat_id, redis_connection, quiz_content)
    new_quiz_question = get_question_content_from_database(
        chat_id, redis_connection)['question']
    update.message.reply_text(f'Новый вопрос:\n{new_quiz_question}')
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
    quiz_content = convert_quiz_files_to_dict()
    redis_connection = redis.Redis(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        password=os.environ['DB_PASSWORD']
        )
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING: [RegexHandler('^Новый вопрос$',
                                   handle_new_question_request)],
            QUESTION_ASKED: [RegexHandler('^Сдаться$', handle_retreat),
                             MessageHandler(
                                 Filters.text, handle_solution_attempt)
                             ]
            },
        fallbacks=[RegexHandler('^Done$', done)]
        )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
