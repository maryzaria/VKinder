import os
from dotenv import load_dotenv


from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import re

# print(re.sub(r'[!?.,<>:''""/]*', '', '"Привет/!!!?>'))


class VkinderBot:
    # текущая сессия ВКонтакте
    vk = None

    # доступ к API ВКонтакте
    vk_api_access = None

    # пометка авторизованности
    authorized = False

    # длительное подключение
    long_poll = None

    # # id пользователя ВКонтакте (например, 1234567890) в виде строки
    # # можно использовать, если диалог будет вестись только с конкретным человеком
    # default_user_id = None
    def __init__(self):
        """
        Инициализация бота при помощи получения доступа к API ВКонтакте
        """
        load_dotenv()
        # авторизация
        self.vk_api_access = self.do_auth()

        if self.vk_api_access is not None:
            self.authorized = True

        # vk = vk_api.VkApi(token=vk_bot_token)
        self.long_poll = VkLongPoll(self.vk)

    def do_auth(self):
        """
        Авторизация за пользователя (не за группу или приложение)
        Использует переменную, хранящуюся в файле настроек окружения .env в виде строки ACCESS_TOKEN="1q2w3e4r5t6y7u8i9o..."
        :return: возможность работать с API
        """
        vk_bot_token = os.getenv('VK_BOT_TOKEN')
        try:
            self.vk = vk_api.VkApi(token=vk_bot_token)
            return self.vk.get_api()
        except Exception as error:
            print(error)
            return None

    def send_msg(self, user_id, text='', keyboard=None, attachment=None):
        """
        Отправляем сообщение пользователю user_id
        :param user_id: кому отправить
        :param text: текст сообщения
        :param keyboard: наличие клавиатуры
        :return: None
        """
        if not self.authorized:
            print("Unauthorized. Check if ACCESS_TOKEN is valid")  #logging
            return

        message = {
            'user_id': user_id,
            'message': text,
            'random_id': randrange(10 ** 7)
        }
        if keyboard:
            message['keyboard'] = keyboard.get_keyboard()

        if attachment:

            # здесь к сообщению прикрепляем фотографии
            message['attachment'] = attachment

            # self.vk.method('messages.send', {
            #     'user_id': event.user_id,
            #     'message': "Имя первого пользователя",
            #     'attachment': attachment,
            #     'random_id': randrange(10 ** 7)
            # })


        try:
            self.vk.method('messages.send', message)
            print(f"Сообщение отправлено для ID {user_id} с текстом: {text}")  # для логирования
        except Exception as error:
            print(error)

    def start_message(self, user_id):
        """Стартовое сообщение"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Начать поиск', color=VkKeyboardColor.SECONDARY)
        self.send_msg(user_id, "Привет! Ты готов начать поиск партнера?", keyboard=keyboard)

    def send_user_photos(self, user_id, new_user_id, user_name, photos=()):
        """ """
        uploader = vk_api.upload.VkUpload(self.vk)
        # передаем список фотографий photos = ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']
        img = uploader.photo_messages(photos)
        attachment = ''
        for photo in img:
            attachment += f"photo{photo['owner_id']}_{photo['id']},"

        # p = {
        #     'type': 'callback_button',
        #     # 'task': self.callback_button,
        #     'user': user_id,
        #     'likes': new_user_id
        # }

        p = {
            "type": "show_snackbar",
            "text": "Покажи исчезающее сообщение на экране"
          }


        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_callback_button(label='Нравится', color=VkKeyboardColor.POSITIVE, payload=p)
        # keyboard.add_button(label='Нравится', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='Стоп', color=VkKeyboardColor.SECONDARY)

        self.send_msg(user_id, user_name, keyboard=keyboard, attachment=attachment)

    @staticmethod
    def callback_button(new_user_id):
        print(new_user_id)

    def run_long_poll(self):
        """
        Запуск бота
        """
        for event in self.long_poll.listen():
            # print(event.type)
            # print('extra_values', event.extra_values)
            # print('flags', event.flags)
            # print(event.extra)
            print(event)
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                # print(event.message_flags)

                msg_text = event.text
                # пользователь нажимает кнопку 'начать' или пишет 'начать' или 'привет'
                if re.sub(r'[!?.,<>:''""/]*', '', msg_text).lower() in ("привет", 'начать'):
                    # метод, собирающий информацию о пользователе
                    # метод, добавляющий пользователя в БД
                    self.start_message(event.user_id)

                elif msg_text in ("Начать поиск", 'Дальше'):
                    # здесь ищем следующего пользователя, отправляем его имя и список фотографий
                    # нужен метод, который возвращает id, имя найденного пользователя и список его фотографий
                    # (обязательно добавить проверку на наличие фотографий при отборе кандидатов)
                    new_user_id = 'new_id'
                    user_name = 'Имя найденного пользователя'
                    photos = ['hearts.jpg', 'vkinder.jpg']
                    self.send_user_photos(event.user_id, new_user_id, user_name, photos=photos)

                elif re.sub(r'[!?.,<>:''""/]*', '', msg_text).lower() in ("пока", "завершить", "до свидания", "стоп", "хватит"):
                    self.send_msg(event.user_id, "Поиск завершен! До свидания🖤")
                else:
                    self.send_msg(event.user_id, "Не понял вашего ответа, попробуйте еще раз")


            # elif event. .payload.get('type') == 'callback_button':
            #     print(event)
            #     print('ураа')




vk = VkinderBot()
vk.run_long_poll()