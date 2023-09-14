import os
import logging
import re
from dotenv import load_dotenv
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from api_vk import VK
from class_next_user import NextUser
from methods import data_base


logging.basicConfig(level=logging.INFO, filename="pylog.log", filemode="a", format="%(asctime)s %(levelname)s %(message)s")
NON_LETTERS = re.compile(r'[!?.,<>:''""/]*')


class VkinderBot:
    # текущая сессия ВКонтакте
    vk = None

    # доступ к API ВКонтакте
    vk_api_access = None

    # пометка авторизованности
    authorized = False

    # длительное подключение
    long_poll = None

    sex, age_from, age_to, city = None, None, None, None

    users_candidates = {}

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
            logging.info('Successful authorization')
            return self.vk.get_api()
        except Exception as error:
            logging.critical(error)
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
            logging.error("Unauthorized. Check if ACCESS_TOKEN is valid")
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
            logging.info(f"Сообщение отправлено для ID {user_id} с текстом: {text}")
        except Exception as error:
            logging.error(error)

    def start_message(self, user_id):
        """Стартовое сообщение"""
        # метод, собирающий информацию о пользователе, если он еще не в БД
        # метод, добавляющий пользователя в БД
        logging.info(f'Пользователь {user_id} внесен в базу данных')
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

    def prefer_sex(self, user_id):
        """Выбор пола"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Женский')
        keyboard.add_button(label='Мужской')
        self.send_msg(user_id, 'Выберите пол будущего партнера', keyboard=keyboard)

    def send_user_photos(self, user_id):
        """Метод для поиска и отправки пользователю потенциального партнера"""
        new_user = next(self.users_candidates[user_id])
        # Здесь проверка, нет ли пользователя с таким id в таблице дизлайков, если есть, заново вызываем next() if new_user not in dislikes:
        new_user_id = new_user.get('id')
        count = 0
        is_blocked = self.newdb.is_blocked(user_id, new_user_id, self.new_session)
        while is_blocked or count > 10:
            new_user = next(self.users_candidates[user_id])
            new_user_id = new_user.get('id')
            is_blocked = self.newdb.is_blocked(user_id, new_user_id, self.new_session)
            count += 1
        user_name = f"{new_user.get('first_name', '')}\n{new_user.get('user_url')}"

        photos = VK().get_photos(owner_id=new_user_id)  # название метода, возвращающего список фотографий вида
        # собираем все фото во вложение
        attachment = ','.join(photos)

        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Нравится', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Не нравится', color=VkKeyboardColor.NEGATIVE)
        # keyboard.add_line()
        # keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
        # keyboard.add_button(label='Стоп', color=VkKeyboardColor.SECONDARY)

        self.send_msg(user_id, user_name, keyboard=keyboard, attachment=attachment)
        # добавляем в БД информацию о кандидате - он был показан
        self.newdb.add_candidate(user_id,
                                 new_user['id'],
                                 new_user['first_name'],
                                 new_user['last_name'],
                                 new_user['sex'],
                                 new_user['city']['title'] if new_user['city'] != '' else '',
                                 new_user['bdate'],
                                 new_user['photo_id'],
                                 new_user['user_url'],
                                 self.new_session)
        return new_user_id

    def continue_conversation(self, user_id):
        """Метод спрашивает, хочет ли пользователь продолжить поиск"""
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='Стоп', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label='Список понравившихся пользователей', color=VkKeyboardColor.SECONDARY)
        self.send_msg(user_id, 'Хотите продолжить поиск?', keyboard=keyboard)

    def like_list(self, user_id, likes):
        """Метод для вывода списка понравившихся пользователей"""
        if not likes:
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_button(label='Дальше', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button(label='Стоп', color=VkKeyboardColor.NEGATIVE)
            self.send_msg(user_id, text='Список пуст. Продолжить поиск?', keyboard=keyboard)
        else:
            for _ in range(len(likes) // 10 + 2):
                likes10 = likes[:10]
                likes = likes[10:]
                send_names = '\n'.join(like[1] for like in likes10)
                send_photos = ','.join(like[0] for like in likes10)
                self.send_msg(user_id, text=send_names, attachment=send_photos)

    def run_long_poll(self):
        """Запуск бота"""
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                # пользователь нажимает кнопку 'начать' или пишет 'начать' или 'привет'
                msg_text = event.text
                user_id = event.user_id
                if NON_LETTERS.sub('', msg_text).lower() in ("привет", 'начать'):
                    new_vk_api = VK()
                    newdict = new_vk_api.get_user_info(user_ids=user_id)
                    # создаем новую бд с параметрами подключения из config.ini
                    self.newdb = data_base('config.ini')
                    # создаем все таблицы
                    self.newdb.build_tables()
                    # открываем новую сессию бд
                    self.new_session = self.newdb.create_session(self.newdb.engine)
                    # добавляем данные пользователя взятые из словаря newdict из метода .get_user_info класса VK api
                    self.newdb.add_user(newdict['user_id'],
                                        newdict['first_name'],
                                        newdict['last_name'],
                                        newdict['sex'],
                                        newdict['bdate'] if 'bdate' in newdict else '31.12.9999',
                                        newdict['city']['title'],
                                        'start',
                                        self.new_session)
                    self.start_message(user_id)
                    # отдельным методом не обновлял статус, при создании новой записи в бд сразу присвоил start
                    self.state = 'start'  # обновить состояние пользователя в БД

                elif msg_text == "Начать поиск" or self.state == 'start':
                    # self.town(user_id)
                    self.send_msg(user_id, 'Введите город, где хотите найти партнера')
                    self.state = 'town'
                    # обновляем состояние пользователя в БД
                    self.newdb.update_state(vk_id=user_id, new_state='town', cursess=self.new_session)

                elif self.state == 'town':
                    self.city = msg_text
                    logging.info(f'Пользователь: {user_id}. Предпочтительный город {self.city} сохранен')
                    # сохраняем выбранный город town в БД
                    self.newdb.prefer_location(vk_id=user_id, location=self.city, cursess=self.new_session)
                    # обновляем состояние пользователя в БД
                    self.newdb.update_state(vk_id=user_id, new_state='age', cursess=self.new_session)
                    self.state = 'age'
                    self.age(user_id)

                elif self.state == 'age':
                    self.age_from, self.age_to = map(int, msg_text.split('-'))
                    # сохраняем выбранный возраст town в БД, учитывая, что возраст в формате '20-30'
                    self.newdb.prefer_age(vk_id=user_id, age_from=self.age_from, age_to=self.age_to, cursess=self.new_session)
                    # обновляем состояние пользователя в БД
                    self.newdb.update_state(vk_id=user_id, new_state='sex', cursess=self.new_session)
                    logging.info(f'Пользователь: {user_id}. Предпочтительный возраст {self.age_from}-{self.age_to} сохранен')
                    self.state = 'sex'
                    self.prefer_sex(user_id)

                elif self.state == 'sex':
                    self.sex = '1' if msg_text == 'Женский' else '2'
                    # сохраняем выбранный пол town в БД
                    self.newdb.prefer_gender(vk_id=user_id, gender=self.sex, cursess=self.new_session)
                    # обновляем состояние пользователя в БД
                    self.newdb.update_state(vk_id=user_id, new_state='search', cursess=self.new_session)
                    logging.info(f'Пользователь: {user_id}. Предпочтительный пол {msg_text}({self.sex}) сохранен')
                    self.state = 'search'
                    self.users_candidates[user_id] = NextUser(user_id=user_id, cursess=self.new_session, db=self.newdb)
                    self.new_user_id = self.send_user_photos(user_id)

                elif NON_LETTERS.sub('', msg_text).lower() in ("пока", "завершить", "до свидания", "стоп", "хватит"):
                    self.state = 'stop'
                    self.send_msg(user_id, f"Поиск приостановлен! До скорой встречи🖤\nЕсли захотите возобновить поиск, напишите ПРИВЕТ или НАЧАТЬ")

                elif msg_text == 'Нравится':
                    # сохраняем пользователя self.new_user_id в таблицу likes
                    self.newdb.like(liker=user_id, liked=self.new_user_id, cursess=self.new_session)
                    logging.info(f'Пользователь {user_id} поставил лайк {self.new_user_id}')
                    self.continue_conversation(user_id)

                elif msg_text == 'Не нравится':
                    # сохраняем пользователя self.new_user_id в таблицу dislikes
                    self.newdb.block(blocker=user_id, blocked=self.new_user_id, cursess=self.new_session)
                    logging.info(f'Пользователь {user_id} поставил дизлайк {self.new_user_id}')
                    self.continue_conversation(user_id)

                elif msg_text == 'Список понравившихся пользователей':
                    self.newdb.update_state(vk_id=user_id, new_state='stop', cursess=self.new_session)
                    likes = self.newdb.show_liked(user_id, self.new_session)
                    self.like_list(user_id, likes)
                    self.state = 'stop'

                elif msg_text == 'Дальше' or self.state == 'search':
                    self.send_user_photos(user_id)

                else:
                    self.send_msg(event.user_id, "Не понял вашего ответа, попробуйте еще раз")
                    logging.error(f'Пользователь {user_id} написал {msg_text}')


if __name__ == '__main__':
    vk = VkinderBot()
    vk.run_long_poll()