import json
import logging
import os
import random

import redis
import vk_api
from dotenv import load_dotenv
from telegram import Bot
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from quiz_question_operations import (convert_quiz_files_to_dict,
                                      get_clear_answer)

logger = logging.getLogger('TelegramLogger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = Bot(token=bot_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_keyboard_to_chat(event, api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Привет, я бот для викторин!'
    )


def handle_new_question_request(event, api, connection, content):
    chat_id = event.user_id
    question, answer = random.choice(list(content.items()))
    clear_answer = get_clear_answer(answer)
    connection.set(chat_id, json.dumps(
        {'question': question, 'answer': clear_answer}))
    api.messages.send(
        user_id=chat_id,
        message=question,
        random_id=get_random_id()
    )


def handle_solution_attempt(event, api, connection):
    chat_id = event.user_id
    correct_answer = json.loads(connection.get(chat_id))['answer']
    if event.text == correct_answer:
        api.messages.send(
            user_id=chat_id,
            message='''Правильно! Поздравляю!
                       Для следующего вопроса нажми «Новый вопрос»”
                       ''',
            random_id=get_random_id()
        )
    else:
        api.messages.send(
            user_id=chat_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=get_random_id()
        )


def handle_retreat(event, api, connection, content):
    chat_id = event.user_id
    correct_answer = json.loads(connection.get(chat_id))['answer']
    api.messages.send(
        user_id=chat_id,
        message=f'Правильный ответ:\n{correct_answer}',
        random_id=get_random_id()
    )
    question, answer = random.choice(list(content.items()))
    clear_answer = get_clear_answer(answer)
    connection.set(chat_id, json.dumps(
        {'question': question, 'answer': clear_answer}))
    api.messages.send(
        user_id=chat_id,
        message=f'Новый вопрос:\n{question}',
        random_id=get_random_id()
    )


def main():
    logging.basicConfig(
        filename='vk_bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
        )
    load_dotenv()
    logger.addHandler(TelegramLogsHandler(
        os.environ['TELEGRAM_BOT_TOKEN'], os.environ['TELEGRAM_CHAT_ID']))
    quiz_content = convert_quiz_files_to_dict()
    redis_connection = redis.Redis(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        password=os.environ['DB_PASSWORD']
    )
    vk_session = vk_api.VkApi(token=os.environ['VK_GROUP_TOKEN'])
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    while True:
        try:
            for vk_event in longpoll.listen():
                if vk_event.type == VkEventType.MESSAGE_NEW and vk_event.to_me:
                    if vk_event.text == '/start':
                        send_keyboard_to_chat(vk_event, vk)
                    elif vk_event.text == 'Новый вопрос':
                        handle_new_question_request(
                            vk_event, vk, redis_connection, quiz_content)
                    elif vk_event.text == 'Сдаться':
                        handle_retreat(
                            vk_event, vk, redis_connection, quiz_content)
                    else:
                        handle_solution_attempt(vk_event, vk, redis_connection)
        except Exception as error:
            logger.exception(
                f'VK bot crushed with exception:')


if __name__ == "__main__":
    main()
