import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3
import os
import datetime as DT
from datetime import datetime
import pandas as pd
import time
import json
from cnfg import bot_token

token = bot_token
bot = telebot.TeleBot(token)
PHOTO_DIR = 'photo'
conn = sqlite3.connect('auctions.db', check_same_thread=False)

Main_keyb_dct = {"Мои аукционы": "menu:my_auc",
                 "Розыгрыш": "menu:lottery",
                 "Топ пользователей": "menu:top",
                 "Правила": "menu:rules",
                 "Статистика": "menu:stats",
                 "Помощь": "menu:help",
                 "Участвовать": "menu:take_part"}
Return_to_menu_keyb_dct = {"Главное меню": "menu:main-menu"}
Trade_inline_keyb_dct = {"+20 p.": "bid:20",
                         "+30 p.": "bid:30",
                         "+50 p.": "bid:50",
                         "+100 p.": "bid:100",
                         "+200 p.": "bid:200",
                         "+500 p.": "bid:500"}


def create_universal_inline_keyb(dct):  # функция для создания клавиатуры главного меню, принимает словарь
    Main_inline_keyb = InlineKeyboardMarkup(row_width=1)
    for key, value in dct.items():
        Main_inline_keyb.add(InlineKeyboardButton(f"{key}", callback_data=f"{value}"))
    return Main_inline_keyb


def create_trade_inline_keyb(dct, lot_id):  # функция для создания клавиатуры торгов, принимает словарь
    Trade_inline_keyb = InlineKeyboardMarkup(row_width=3)
    for key, value in dct.items():
        Trade_inline_keyb.add(InlineKeyboardButton(f"{key}", callback_data=f"{value}:{lot_id}"))
    Trade_inline_keyb.add(InlineKeyboardButton("Авто-ставка", callback_data=f"bid:auto-bid:{lot_id}"))
    Trade_inline_keyb.add(InlineKeyboardButton("Старт", callback_data=f"trade:start_auction:{lot_id}"))
    Trade_inline_keyb.add(InlineKeyboardButton("\U0001F552", callback_data=f"trade:timeleft:{lot_id}"),
                          InlineKeyboardButton("\U00002139", callback_data=f"trade:info:{lot_id}"))
    return Trade_inline_keyb


Trade_inline_keyb = InlineKeyboardMarkup(row_width=3)
Trade_inline_keyb.add(InlineKeyboardButton("+20 p.", callback_data="bid:20"),
                      InlineKeyboardButton("+30 p.", callback_data="bid:30"),
                      InlineKeyboardButton("+50 p.", callback_data="bid:50"),
                      InlineKeyboardButton("+100 p.", callback_data="bid:100"),
                      InlineKeyboardButton("+200 p.", callback_data="bid:200"),
                      InlineKeyboardButton("+500 p.", callback_data="bid:500"))
"""Прописать условие для автоставки (В кошельке 500р)"""
Trade_inline_keyb.add(InlineKeyboardButton("Авто-ставка", callback_data="bid:auto-bid"))
Trade_inline_keyb.add(InlineKeyboardButton("Старт", callback_data="trade:start_auction"))
Trade_inline_keyb.add(InlineKeyboardButton("\U0001F552", callback_data="trade:timeleft"),
                      InlineKeyboardButton("\U00002139", callback_data="trade:info"))


@bot.message_handler(commands=['start'])
def start(message):
    # print(message)
    if message.text == "/start":
        bot.send_message(message.chat.id,
                         "Привет, я бот аукционов @coin_minsk. Я помогу Вам следить за выбранными лотами,"
                         "и регулировать ход аукциона. А так же буду следить за Вашими накопленными балами. "
                         "Удачных торгов 🤝", reply_markup=create_universal_inline_keyb(Main_keyb_dct))
    else:
        print(message.text)
        lot_id = message.text.split(' ')[1]
        print("id LOTa", lot_id)
        with conn:
            name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
        result = f"Название лота: {name[0]}\n" \
                 f"Описание: {description[0]}\n" \
                 f"Стартовая цена: {start_price[0]} руб.\n" \
                 f"Расположение продавца: {geolocations[0]}\n" \
                 f"Продавец: {link_seller[0]}\n"
        print(result)
        with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                photo_1[0]), "rb") as img:
            bot.send_photo(message.chat.id, photo=img, caption=result,
                           reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct, lot_id))

        # по клику на кнопку "Участвовать" запишем юзера в базу клиентов
        user_telegram_id = message.from_user.id
        user_first_name = message.from_user.first_name
        user_telegram_username = message.from_user.username
        user_last_name = message.from_user.last_name
        with conn:
            conn.execute("INSERT OR IGNORE INTO Clients (full_name, telegram_id) "
                         "VALUES (?, ?)",
                         (user_first_name, user_telegram_id))  # добавьте новую запись в таблицу "Отзывы"
        conn.commit()  # сохраняем изменения в базе данных


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, )
    print(call.data.split(':'))
    if call.data.split(':')[0] == "take_part2":
        lot_id = call.data.split(':')[1]
        print("id LOTa", lot_id)
        with conn:
            name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")]
        result = f"Название лота: {name[0]}\n" \
                 f"Описание: {description[0]}\n" \
                 f"Стартовая цена: {start_price[0]} руб.\n" \
                 f"Расположение продавца: {geolocations[0]}\n" \
                 f"Ссылка на продавца: {link_seller[0]}\n"
        with open("photo/" + photo_1[0], "rb") as img:
            bot.send_photo(call.message.chat.id, photo=img, caption=result, reply_markup=Trade_inline_keyb)
        # bot.send_message(call.message.chat.id, f"{result}", reply_markup=Trade_inline_keyb)
        bot.send_message(chat_id='@coin_minsk', text=f'{result}',
                         parse_mode="Markdown", reply_markup=Trade_inline_keyb)

    if call.data.split(':')[1] == "main-menu":
        bot.edit_message_text("Привет, я бот аукционов @coin_minsk. Я помогу Вам следить за "
                              "выбранными лотами, и регулировать ход аукциона. А так же буду следить "
                              "за Вашими накопленными балами. Удачных торгов 🤝",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Main_keyb_dct))

    if call.data.split(':')[1] == "info":
        print("Отправляем всплывающее окно с текстом")
        bot.answer_callback_query(call.id, "Делая ставку участник подтверждает желание и возможность выкупить лот. В "
                                           "случае невыкупа лота в течение 3-х суток, участник блокируется.",
                                  show_alert=True)
    if call.data.split(':')[1] == "timeleft":
        print("Отправляем выезжающее окно с текстом - время аукциона")
        current_datetime = DT.datetime.now()
        with conn:
            start_time1 = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            end_time2 = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
        start_time = datetime.strptime(str(current_datetime)[:19], "%Y-%m-%d %H:%M:%S")  # 2021-10-01 12:00:00
        end_time = datetime.strptime(end_time2[0], "%Y-%m-%d %H:%M:%S")
        timedelta = pd.Timestamp(end_time) - pd.Timestamp(start_time)
        bot.answer_callback_query(call.id, f"Осталось времени: "
                                           f"{timedelta.components.days} дней "
                                           f"{timedelta.components.hours} часов "
                                           f"{timedelta.components.minutes} минут "
                                           f"{timedelta.components.seconds} секунд", show_alert=False)

    if call.data.split(':')[1] == "rules":
        print("Отправляем текст c правилами")
        bot.edit_message_text("После окончания торгов, победитель или продавец должны выйти на связь "
                              "в течении суток‼️Победитель обязан выкупить лот в течении ТРЁХ дней "
                              "после окончания аукциона🔥НЕ ВЫКУП ЛОТА - ПЕРМАНЕНТНЫЙ БАН ВО ВСЕХ "
                              "НУМИЗМАТИЧЕСКИХ СООБЩЕСТВАХ И АУКЦИОНАХ🤬 Чтобы узнать время "
                              "окончания аукциона, нажмите на ⏰ Анти снайпер - Ставка сделанная за 5 "
                              "минут до конца, автоматически переносит Аукцион на 5 минут вперёд "
                              "‼️Работают только проверенные продавцы. Дополнительные Фото можно "
                              "запросить у продавца. Случайно сделал ставку?🤔 Напиши продавцу‼️ "
                              "Отправка почтой, стоимость пересылки зависит от общего веса "
                              "отправления и страны. Обсуждается с продавцом. Лоты можно копить,"
                              "экономя при этом на почте. Отправка в течении трёх дней после оплаты‼️",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    if call.data.split(':')[1] == "help":
        print("Отправляем текст c help")
        bot.edit_message_text("Свяжитесь с нами, если у вас возникли вопросы 'ссылка на телегу админа'"
                              "Удачных торгов и выгодных покупок!",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    # if call.data.split(':')[0] == "bid":
    #     current_bid = call.data.split(':')[1]
    #     current_lot_id = call.data.split(':')[2]
    #     print(current_bid)
    #     print(current_lot_id)
    #     try:
    #         with conn:
    #             # Получаем JSON-строку
    #             trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
    #     except Exception as e:
    #         print(e)
    #     trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
    #     # Добавляем данные по торгам и ставке клиента в объект (словарь)
    #     user_telegram_username = call.message.from_user.username
    #     trade_info[user_telegram_username] = [current_bid, max_price]
    #     trade_info_str = json.dumps(trade_info)
    #     trades_status = 'in progress'
    #     with conn:
    #         conn.execute("INSERT OR IGNORE INTO Trades (lots_id, trade_info, trades_status) "
    #                      "VALUES (?, ?, ?)",
    #                      (callback_Lots_id, trade_info_str, trades_status))  # добавьте новую запись в таблицу "Trades"
    #     conn.commit()  # сохраняем изменения в базе данных


# """___________________________________________________________________"""
# cursor = conn.cursor()
# # Функция для проверки изменений в базе данных
# def check_db():
#     cursor.execute("SELECT COUNT(*) FROM Lots")  # Запрашиваем количество записей в таблице Lots
#     count = cursor.fetchone()[0]
#     # Возвращаем True, если количество изменилось, иначе False
#     global prev_count
#     if count != prev_count:
#         prev_count = count
#         return True
#     else:
#         return False
# # Функция для отправки сообщения об изменениях в базе данных
# def send_message():
#     cursor.execute("SELECT * FROM Lots ORDER BY id DESC LIMIT 1")  # Запрашиваем последнюю запись в таблице Lots
#     lot = cursor.fetchone()
#     # Формируем текст сообщения с данными пользователя
#     text = f"Новый lot в базе данных:\nID: {lot[0]}\nИмя: {lot[1]}\nОписание: {lot[2]}"
#     bot.send_message(chat_id='@coin_minsk', text=text)
#     print("NEW LOT NEW LOT", text)
# prev_count = 0  # Переменная для хранения предыдущего количества записей в базе данных
# while True:  # Бесконечный цикл для мониторинга базы данных
#     if check_db():  # Проверяем, есть ли изменения в базе данных
#         send_message()  # Если есть, то отправляем сообщение о них
#     time.sleep(5)  # Ждем х секунд перед следующей проверкой
# """___________________________________________________________________"""


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
