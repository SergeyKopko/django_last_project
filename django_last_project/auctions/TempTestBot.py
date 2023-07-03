import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3
import os
import datetime as DT
from datetime import datetime
import time
import json

token = '6112420224:AAF0gLi1ZFYabFDubwjawFyjDMjmtJ0_JZc'
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


def create_universal_inline_keyb(dct):  # функция для создания клавиатуры для добавления блюда в БД, принимает словарь
    Main_inline_keyb = InlineKeyboardMarkup(row_width=1)
    for key, value in dct.items():
        Main_inline_keyb.add(InlineKeyboardButton(f"{key}", callback_data=f"{value}"))
    return Main_inline_keyb


Trade_inline_keyb = InlineKeyboardMarkup(row_width=3)
Trade_inline_keyb.add(InlineKeyboardButton("+20p:", callback_data="bid:+20"),
                      InlineKeyboardButton("+30p:", callback_data="bid:+30"),
                      InlineKeyboardButton("+50p:", callback_data="bid:+50"),
                      InlineKeyboardButton("+100p:", callback_data="bid:+100"),
                      InlineKeyboardButton("+200p:", callback_data="bid:+200"),
                      InlineKeyboardButton("+500p:", callback_data="bid:+500"))
"""Прописать условие для автоставки (В кошельке 500р)"""
Trade_inline_keyb.add(InlineKeyboardButton("Авто-ставка", callback_data="qwerty:qwerty"))
Trade_inline_keyb.add(InlineKeyboardButton("Старт", callback_data="qwerty:qwerty"))
Trade_inline_keyb.add(InlineKeyboardButton("\U0001F552", callback_data="qwerty:timeleft"),
                      InlineKeyboardButton("\U00002139", callback_data="qwerty:info"))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет, я бот аукционов @coin_minsk. Я помогу Вам следить за выбранными лотами,"
                     "и регулировать ход аукциона. А так же буду следить за Вашими накопленными балами. "
                     "Удачных торгов 🤝", reply_markup=create_universal_inline_keyb(Main_keyb_dct))
    # user_telegram_id = message.from_user.id


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, )
    if call.data.split(':')[1] == "take_part":
        with conn:
            name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = 1")]

        result = f"Название лота: {name[0]}\n" \
                 f"Описание: {description[0]}\n" \
                 f"Стартовая цена: {start_price[0]} руб.\n" \
                 f"Расположение продавца: {geolocations[0]}\n" \
                 f"Ссылка на продавца: {link_seller[0]}\n"

        with open("photo/" + photo_1[0], "rb") as img:
            bot.send_photo(call.message.chat.id, photo=img)
        bot.send_message(call.message.chat.id, f"{result}", reply_markup=Trade_inline_keyb)
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
        difference = end_time - start_time
        days = difference.days  # Получаем целое количество дней из объекта timedelta
        total_seconds = difference.total_seconds()  # Получаем общее количество секунд из объекта timedelta
        hours = int(total_seconds // 3600)  # Преобразуем общее количество секунд в часы, минуты и секунды
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        bot.answer_callback_query(call.id, f"Осталось времени: "
                                           f"{days} дней "
                                           f"{hours} часов "
                                           f"{minutes} минут "
                                           f"{seconds} секунд", show_alert=False)

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

# import requests
# channel = "@coin_minsk"  # название вашего канала
# photo = "photo/1.jpg"
# text = "This is a test message" # текст сообщения
# buttons = [[{"text": "Share", "url": "t.me/your_channel?start=your_post_id"}], # кнопка для пересылки
#            [{"text": "Visit website", "url": "https://example.com"}]] # кнопка для перехода на сайт
# data = {
#     "chat_id": channel,
#     "photo": photo,
#     "caption": text,
#     "reply_markup": {"inline_keyboard": buttons}
# }
# response = requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", json=data)
# print(response.json())


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
