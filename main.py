from config import TOKEN
from models.database import Session
from sqlalchemy import and_
from telebot import types

import telebot
import re
import requests
import json

from models.user import User

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.send_message(message.chat.id,
                           'Для использования бота войдите или зарегистрируйтесь по номеру телефона.',
                           reply_markup=main_menu())
    bot.register_next_step_handler(msg, choosing_action)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Рандомная картинка":
        r = requests.get('https://api.thecatapi.com/v1/images/search')
        url = json.loads(r.content.decode('UTF-8'))[0]['url']
        bot.send_photo(message.chat.id, url)
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')


def choosing_action(message):
    if message.text == "Вход":
        msg = bot.send_message(message.chat.id, 'Введите ваш номер телефона', reply_markup=back_menu())
        bot.register_next_step_handler(msg, input_phone, "login")
    elif message.text == "Регистрация":
        msg = bot.send_message(message.chat.id, 'Введите ваш номер телефона', reply_markup=back_menu())
        bot.register_next_step_handler(msg, input_phone, "register")
    else:
        msg = bot.send_message(message.chat.id, 'Выберите действие "Вход" или "Регистрация"')
        bot.register_next_step_handler(msg, choosing_action)


def login_user(message):
    session = Session()
    result = session.query(User).filter(User.phone == int(message.text)).count()
    if result == 0:
        session.close()
        msg = bot.send_message(message.chat.id, 'Этот номер телефона не зарегистрирован!', reply_markup=main_menu())
        bot.register_next_step_handler(msg, choosing_action)
    else:
        result = session.query(User).filter(and_(User.phone == int(message.text), (User.chat_id == message.chat.id))).count()
        if result == 0:
            session.close()
            msg = bot.send_message(message.chat.id, 'Ошибка авторизации!', reply_markup=main_menu())
            bot.register_next_step_handler(msg, choosing_action)
        else:
            session.close()
            bot.send_message(message.chat.id, 'Успешная авторизация', reply_markup=get_image_menu())


def register_user(message):
    session = Session()
    result = session.query(User).filter(User.phone == int(message.text)).count()
    if result == 0:
        user = User(
            phone=int(message.text),
            chat_id=message.chat.id
        )
        session.add(user)
        session.commit()
        session.close()
        msg = bot.send_message(message.chat.id, 'Регистрация прошла успешно', reply_markup=main_menu())
        bot.register_next_step_handler(msg, choosing_action)
    else:
        session.close()
        msg = bot.send_message(message.chat.id, 'Этот номер телефона уже используется!', reply_markup=main_menu())
        bot.register_next_step_handler(msg, choosing_action)


def input_phone(message, operation_type):
    if message.text == "Назад":
        msg = bot.send_message(message.chat.id, 'Выберите действие "Вход" или "Регистрация"',
                               reply_markup=main_menu())
        bot.register_next_step_handler(msg, choosing_action)
    else:
        if valid_phone(message.text):
            if message.text[0] == "+":
                message.text = message.text[1:]
            login_user(message) if operation_type == "login" else register_user(message)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Недопустимый формат! Попробуйте ввести номер телефона ещё раз')
            bot.register_next_step_handler(msg, input_phone, operation_type)


def convert_record_to_list(record):
    return str(record).split(', ')


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    login_button = types.KeyboardButton('Вход')
    register_button = types.KeyboardButton('Регистрация')
    markup.row(login_button)
    markup.row(register_button)
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton('Назад')
    markup.row(back_button)
    return markup


def get_image_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    image_button = types.KeyboardButton('Рандомная картинка')
    markup.row(image_button)
    return markup


def remove_menu():
    markup = types.ReplyKeyboardRemove()
    return markup


def valid_phone(number):
    regex = r'\+?\d{11,13}'
    return re.fullmatch(regex, number)


bot.polling(none_stop=True)
