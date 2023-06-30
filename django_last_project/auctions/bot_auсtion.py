import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3
import os
import datetime as DT
import time
import json



token = '5937676517:AAEG8U11wayyFFQmbJKi3Y3BdINCzUTIDWs'
bot = telebot.TeleBot(token)
PHOTO_DIR = 'photo'
conn = sqlite3.connect('auctions.db', check_same_thread=False)



Trade_inline_keyb = InlineKeyboardMarkup(row_width=3)
Trade_inline_keyb.add(InlineKeyboardButton("+20p:", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("+30p:", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("+50p:", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("+100p:", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("+200p:", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("+500p:", callback_data="qwerty:qwerty")) # неактивные кнопки с фиктивным колбэком

"""Прописать условие для автоставки(В кошельке 500р)"""

Trade_inline_keyb.add(InlineKeyboardButton("Автос-тавка", callback_data="qwerty:qwerty"))
Trade_inline_keyb.add(InlineKeyboardButton("\U0001F552", callback_data="qwerty:qwerty"),
                      InlineKeyboardButton("Инфа", callback_data="qwerty:qwerty"))

Main_inline_keyb = InlineKeyboardMarkup()
Main_inline_keyb.add(InlineKeyboardButton("Мои аукционы", callback_data="menu:txt1"))
Main_inline_keyb.add(InlineKeyboardButton("Розыгрыш", callback_data="menu:txt3"))
Main_inline_keyb.add(InlineKeyboardButton("Топ пользователей", callback_data="menu:txt4"))
Main_inline_keyb.add(InlineKeyboardButton("Правила", callback_data="menu:txt2"))
Main_inline_keyb.add(InlineKeyboardButton("Статистика", callback_data="menu:profile"))
Main_inline_keyb.add(InlineKeyboardButton("Помощь", callback_data="menu:profile"))
Main_inline_keyb.add(InlineKeyboardButton("Участвовать", callback_data="take:part"))



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет ,я бот аукционов @opt_monet_vtelege Я помогу вам следить за выбранными лотами,"
                                      "и регулировать ход аукциона.А так же буду следить за вашими накопленными балами. "
                                      "Удачных торгов 🤝", reply_markup=Main_inline_keyb)
    user_telegram_id = message.from_user.id


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    if call.data.split(':')[1] == "part":
        with conn:
            name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            photo = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]

        result = f"{name[0]}\n" \
                 f"{description[0]}\n" \
                 f"{start_price[0]}\n" \
                 f"{link_seller[0]}\n" \
                 f"{geolocations[0]}\n"
        with open("photo/" + photo[0], "rb") as img:
            bot.send_photo(call.message.chat.id, photo=img)
        bot.send_message(call.message.chat.id, f"{result}", reply_markup=Trade_inline_keyb)


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
