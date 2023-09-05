import os
from dotenv import load_dotenv


from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
import re


class VkinderBot:
    # текущая сессия ВКонтакте
    vk = None

    # доступ к API ВКонтакте
    vk_api_access = None

    # пометка авторизованности
    authorized = False

    # длительное подключение
    long_poll = None

    def __init__(self):
        """ Инициализация бота при помощи получения доступа к API ВКонтакте """
        load_dotenv()
        # авторизация
        self.vk_api_access = self.do_auth()

        if self.vk_api_access is not None:
            self.authorized = True

        self.long_poll = VkLongPoll(self.vk)

        self.state = None

        self.new_user_id = None

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
        :param attachment: наличие вложений
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

        try:
            self.vk.method('messages.send', message)
            print(f"Сообщение отправлено для ID {user_id} с текстом: {text}")  # для логирования
        except Exception as error:
            print(error)

    def start_message(self, user_id):
        """Стартовое сообщение"""
        # метод, собирающий информацию о пользователе
        # метод, добавляющий пользователя в БД
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Начать поиск', color=VkKeyboardColor.SECONDARY)
        self.send_msg(user_id, "Привет! Ты готов начать поиск партнера?", keyboard=keyboard)

    def age(self, user_id):
        """Клавиатура для выбора возраста"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='20-30')
        keyboard.add_button(label='30-40')
        keyboard.add_line()
        keyboard.add_button(label='40-50')
        keyboard.add_button(label='50-60')
        self.send_msg(user_id, 'Выберите возрастную категорию', keyboard=keyboard)

    def sex(self, user_id):
        """Выбор пола"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Женский')
        keyboard.add_button(label='Мужской')
        self.send_msg(user_id, 'Выберите пол будущего партнера', keyboard=keyboard)

    def send_user_photos(self, user_id):
        """Метод для поиска и отправки пользователю потенциального партнера"""
        # здесь вызываем метод, который осуществляет поиск подходящих пользователей.
        # чтобы не делать поиск каждый раз, когда вызывается этот метод, в метод поиска добавляем проверку: если список существует, поиск не делаем.
        # Критерии поиска достаем из БД
        # Потом выдаем информацию (словарь) о следующем пользователе и список фотографий (обязательно добавить проверку на наличие фотографий при отборе кандидатов)

        new_user = {}  # next() - метод, выдающий следующего пользователя из списка (словарь данных о нем)
        # Здесь проверка, нет ли пользователя с таким id в таблице дизлайков, если есть, заново вызываем next() if new_user not in dislikes:

        self.new_user_id = 'new_id'  # new_user.get('id')
        user_name = 'Имя найденного пользователя'  # new_user.get('username')
        photos = ['photo-222321058_457239077']  # название метода, возвращающего список фотографий вида
        # photos = [f"photo{photo['owner_id']}_{photo['id']}", f"photo{photo['owner_id']}_{photo['id']}", f"photo{photo['owner_id']}_{photo['id']}"]

        # собираем все фото во вложение
        attachment = ','.join(photos)

        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Нравится', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE)
        # keyboard.add_line()
        # keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
        # keyboard.add_button(label='Стоп', color=VkKeyboardColor.SECONDARY)

        self.send_msg(user_id, user_name, keyboard=keyboard, attachment=attachment)

    def continue_conversation(self, user_id):
        """Метод спрашивает, хочет ли пользователь продолжить поиск"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='Стоп', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label='Список понравившихся пользователей', color=VkKeyboardColor.SECONDARY)
        self.send_msg(user_id, 'Хотите продолжить поиск?', keyboard=keyboard)

    def like_list(self, user_id):
        """Метод для вывода списка понравившихся пользователей"""
        likes = [] # здесь нужен метод, который вернет список понравившихся пользователей: имя и их фото (кортеж)
        if not likes:
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button(label='Стоп', color=VkKeyboardColor.NEGATIVE)
            self.send_msg(user_id, text='Список пуст. Продолжить поиск?', keyboard=keyboard)
        else:
            for like in likes:
                name, photo = like
                self.send_msg(user_id, text=name, attachment=photo)

    def run_long_poll(self):
        """Запуск бота"""
        for event in self.long_poll.listen():
            # print(event)
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg_text = event.text
                id = event.user_id
                # print(msg_text)
                print(self.state)
                # пользователь нажимает кнопку 'начать' или пишет 'начать' или 'привет'
                if re.sub(r'[!?.,<>:''""/]*', '', msg_text).lower() in ("привет", 'начать'):
                    self.start_message(id)
                    self.state = 'start'  # обновить состояние пользователя в БД

                elif msg_text == "Начать поиск" or self.state == 'start':
                    # self.town(id)
                    self.send_msg(id, 'Введите город, где хотите найти партнера')

                    self.state = 'town'

                elif self.state == 'town':
                    town = msg_text
                    print(f'Город {town} сохранен')
                    # сохраняем выбранный город town в БД
                    # обновляем состояние пользователя в БД
                    self.state = 'age'
                    self.age(id)

                elif self.state == 'age':
                    age = msg_text
                    print(f'Возраст {age} сохранен')
                    # сохраняем выбранный возраст town в БД
                    # обновляем состояние пользователя в БД
                    self.state = 'sex'
                    self.sex(id)

                elif self.state == 'sex':
                    sex = msg_text
                    print(f'Пол {sex} сохранен')
                    # сохраняем выбранный пол town в БД
                    # обновляем состояние пользователя в БД
                    self.state = 'search'
                    self.send_user_photos(id)

                elif re.sub(r'[!?.,<>:''""/]*', '', msg_text).lower() in ("пока", "завершить", "до свидания", "стоп", "хватит"):
                    self.state = 'stop'
                    self.send_msg(id, f"Поиск приостановлен! До скорой встречи🖤\nЕсли захотите возобновить поиск, напишите ПРИВЕТ или НАЧАТЬ")

                elif msg_text == 'Нравится':
                    # сохраняем пользователя self.new_user_id в таблицу likes
                    print(f'{self.new_user_id} нравится {id}')
                    self.continue_conversation(id)

                elif msg_text == 'Не нравится':
                    # сохраняем пользователя self.new_user_id в таблицу dislikes
                    print(f'{self.new_user_id} не нравится {id}')
                    self.continue_conversation(id)

                elif msg_text == 'Список понравившихся пользователей':
                    self.like_list(id)
                    self.state = 'stop'

                elif msg_text == 'Дальше' or self.state == 'search':
                    self.send_user_photos(id)

                else:
                    self.send_msg(event.user_id, "Не понял вашего ответа, попробуйте еще раз")


if __name__ == '__main__':
    vk = VkinderBot()
    vk.run_long_poll()