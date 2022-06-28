import logging
import os
import random
import traceback

import vk_api
from dotenv import load_dotenv
from telegram import Bot
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = Bot(token=bot_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_keybord_to_chat(event, api):
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


def echo(event, api):
    api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


if __name__ == "__main__":
    logging.basicConfig(
        # filename='vk_bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.ERROR
        )
    load_dotenv()
    vk_session = vk_api.VkApi(token=os.environ['VK_GROUP_TOKEN'])
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger = logging.getLogger('TelegramLogger')
    logger.addHandler(TelegramLogsHandler(
        os.environ['TELEGRAM_BOT_TOKEN'], os.environ['TELEGRAM_CHAT_ID']))
    while True:
        try:
            for vk_event in longpoll.listen():
                if vk_event.type == VkEventType.MESSAGE_NEW and vk_event.to_me:
                    if vk_event.text == 'start':
                        send_keybord_to_chat(vk_event, vk)
                    else:
                        echo(vk_event, vk)
        except Exception as error:
            logging.error(traceback.format_exc())
            # logger.error(
            #     f'VK bot crushed with exception:\n{traceback.format_exc()}')
