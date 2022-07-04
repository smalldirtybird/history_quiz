import json
import os
import random
from functools import partial
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler, Updater)

from quiz_question_operations import (convert_quiz_files_to_dict,
                                      get_clear_answer,
                                      get_question_content_from_database)

WAITING, QUESTION_ASKED = range(2)


def start(bot, update):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text='Привет, я бот для викторин!',
                     reply_markup=reply_markup)
    return WAITING


def handle_new_question_request(bot, update, connection, content):
    chat_id = update['message']['chat']['id']
    question, answer = random.choice(list(content.items()))
    clear_answer = get_clear_answer(answer)
    connection.set(chat_id, json.dumps({'question': question, 'answer': clear_answer}))
    update.message.reply_text(question)
    return QUESTION_ASKED


def handle_solution_attempt(bot, update, connection):
    chat_id = update['message']['chat']['id']
    correct_answer = get_question_content_from_database(
        chat_id, connection)['answer']
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


def handle_retreat(bot, update, connection, content):
    chat_id = update['message']['chat']['id']
    correct_answer = get_question_content_from_database(
        chat_id, connection)['answer']
    bot.send_message(chat_id=update['message']['chat']['id'],
                     text=f'Правильный ответ:\n{correct_answer}')
    question, answer = random.choice(list(content.items()))
    clear_answer = get_clear_answer(answer)
    connection.set(chat_id, json.dumps({'question': question, 'answer': clear_answer}))
    update.message.reply_text(f'Новый вопрос:\n{question}')
    return QUESTION_ASKED


def done(bot, update):
    update.message.reply_text("Пока, до следующего раза!")
    return ConversationHandler.END


def main():
    load_dotenv()
    quiz_content = convert_quiz_files_to_dict()
    redis_connection = redis.Redis(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        password=os.environ['DB_PASSWORD']
    )
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dp = updater.dispatcher
    new_question_request = partial(handle_new_question_request,
                                   connection=redis_connection,
                                   content=quiz_content)
    solution_attempt = partial(handle_solution_attempt,
                               connection=redis_connection)
    retreat = partial(handle_retreat,
                      connection=redis_connection,
                      content=quiz_content)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING: [RegexHandler('^Новый вопрос$',
                                   new_question_request)],
            QUESTION_ASKED: [RegexHandler('^Сдаться$', retreat),
                             MessageHandler(
                                 Filters.text, solution_attempt)
                             ]
        },
        fallbacks=[RegexHandler('^Done$', done)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
