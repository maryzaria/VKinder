import os
from dotenv import load_dotenv


load_dotenv()
vk_bot_token = os.getenv('VK_BOT_TOKEN')

from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

token = os.getenv('VK_BOT_TOKEN')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message, keyboard=None):
    message = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7)
    }
    if keyboard:
        message['keyboard'] = keyboard.get_keyboard()
    vk.method('messages.send', message)




for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg_text = event.text

            if msg_text.lower() in ("привет", 'начать'):
                keyboard = VkKeyboard(one_time=False, inline=True)
                keyboard.add_button(label='Начать поиск', color=VkKeyboardColor.SECONDARY)
                write_msg(event.user_id, "Привет!", keyboard=keyboard)

            elif msg_text == "Начать поиск":
                keyboard = VkKeyboard(one_time=False, inline=True)
                keyboard.add_button(label='Нравится', color=VkKeyboardColor.POSITIVE)
                keyboard.add_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE)

                write_msg(event.user_id, "Пользователь1", keyboard)

            elif msg_text == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
