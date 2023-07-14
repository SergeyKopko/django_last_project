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
from cnfg import bot_token_dima

# import django
# from django_last_project.auctions.auction_website.models import Traids
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
# django.setup()
# trade = Traids.objects.create(lots=1, trade_info="description", traids_status="traids_status")
# trade.save()



token = bot_token_dima
bot = telebot.TeleBot(token)
PHOTO_DIR = 'photo'
conn = sqlite3.connect('auctions.db', check_same_thread=False)

Main_keyb_dct = {"Мои аукционы": "menu:my_auc",
                 "Розыгрыш": "menu:lottery",
                 "Топ пользователей": "menu:top",
                 "Правила": "menu:rules",
                 "Статистика": "menu:stats",
                 "Помощь": "menu:help"}
Return_to_menu_keyb_dct = {"Главное меню": "menu:main-menu"}
Trade_inline_keyb_dct = {"+20 p.": "bid:20",
                         "+30 p.": "bid:30",
                         "+50 p.": "bid:50",
                         "+100 p.": "bid:100",
                         "+200 p.": "bid:200",
                         "+500 p.": "bid:500"}


# Функция для проверки изменений в базе данных
def check_db(lot, count, last, user_telegram_id):
    print("лот", lot, user_telegram_id)
    try:
        with conn:
            # Получаем JSON-строку
            trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {lot}")][0]
    except Exception as e:
        print(e)
    trade_info = json.loads(trade_info_str)
    print("Инфа по торгам из функции проверки базы", trade_info)
    current_count_bid = len(trade_info["bid_history"])
    current_last_bid = trade_info["bid_history"][-1]
    print("количество ставок из update", count, "текущее количество после проверки", current_count_bid)
    # Возвращаем True, если количество изменилось, иначе False
    if current_count_bid > count and user_telegram_id != current_last_bid:
        return True
    else:
        return False


def create_universal_inline_keyb(dct):  # функция для создания клавиатуры главного меню, принимает словарь
    Main_inline_keyb = InlineKeyboardMarkup(row_width=1)
    for key, value in dct.items():
        Main_inline_keyb.add(InlineKeyboardButton(f"{key}", callback_data=f"{value}"))
    return Main_inline_keyb


def create_trade_inline_keyb(dct, lot_id):  # функция для создания клавиатуры торгов, принимает словарь
    Trade_inline_keyb = InlineKeyboardMarkup(row_width=3)
    trade_buttons = []
    for key, value in dct.items():
        trade_buttons.append(InlineKeyboardButton(f"{key}", callback_data=f"{value}:{lot_id}"))
    Trade_inline_keyb.add(*trade_buttons)
    try:
        with conn:
            user_wallet_info = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {lot_id}")][0]
            trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {lot_id}")][
                0]  # Получаем JSON-строку
    except Exception as e:
        print(e)
    if user_wallet_info >= 500:
        Trade_inline_keyb.add(InlineKeyboardButton("Авто-ставка", callback_data=f"bid:auto-bid:{lot_id}"))
    bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
    if len(bids_dct) == 0:
        Trade_inline_keyb.add(InlineKeyboardButton("Старт", callback_data=f"trade:start_auction:{lot_id}"))
    Trade_inline_keyb.add(InlineKeyboardButton("Обновить", callback_data=f"trade:update_auction:{lot_id}"))
    Trade_inline_keyb.add(InlineKeyboardButton("\U0001F552", callback_data=f"trade:timeleft:{lot_id}"),
                          InlineKeyboardButton("\U00002139", callback_data=f"trade:info:{lot_id}"))
    return Trade_inline_keyb


@bot.message_handler(commands=['start'])
def start(message):
    # print(message)
    if message.text == "/start":
        bot.send_message(message.chat.id,
                         "Привет, я бот аукционов @coin_minsk. Я помогу Вам следить за выбранными лотами,"
                         "регулировать ход аукциона и следить за Вашими накопленными балами. "
                         "Удачных торгов! 🤝", reply_markup=create_universal_inline_keyb(Main_keyb_dct))
    if message.text[0:6] == "/start" and len(message.text) > 5:
        print(message.text)
        # global lot_id
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
        result = f"Номер лота: {lot_id}\n" \
                 f"Название лота: {name[0]}\n" \
                 f"Описание: {description[0]}\n" \
                 f"Стартовая цена: {start_price[0]} руб.\n" \
                 f"Расположение продавца: {geolocations[0]}\n" \
                 f"Продавец: {link_seller[0]}\n"
        print(result)
        current_datetime = DT.datetime.now()
        print(current_datetime)
        # timedelta = pd.Timestamp(end_time) - pd.Timestamp(start_time)
        if datetime.strptime(str(current_datetime)[:19], "%Y-%m-%d %H:%M:%S") < datetime.strptime(end_time[0][:19], "%Y-%m-%d %H:%M:%S"):
            print("аук еще продолжается")
            with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                    photo_1[0]), "rb") as img:
                bot.send_photo(message.chat.id, photo=img, caption=result,
                               reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct, lot_id))
            # по клику на кнопку "Участвовать" запишем юзера в базу клиентов
            user_telegram_id = message.from_user.id
            user_first_name = message.from_user.first_name
            try:
                with conn:
                    conn.execute("INSERT OR IGNORE INTO Clients (full_name, telegram_id, try_strike) VALUES (?, ?, ?)",
                                 (user_first_name, user_telegram_id, 0))
                conn.commit()
            except Exception as e:
                print(e)
        else:
            print("аук завершен")
            try:
                with conn:
                    trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                 f"{lot_id}")][0]
            except Exception as e:
                print(e)
            trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
            msg_id = trade_info["bid_history"][0]
            print("Инфа по торгам", trade_info)
            if len(trade_info["bid_history"]) > 1:
                winner_id = trade_info["bid_history"][-1]
                with conn:
                    winner_name = [i[1] for i in conn.execute(
                        f"SELECT * FROM Clients WHERE telegram_id = {winner_id}")][0]
            else:
                winner_name = "Победителей нет."

            result += f"\n\U0001F3C1Аукцион завершен.\nПобедитель: {winner_name}"
            with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                    photo_1[0]), "rb") as img:
                bot.send_photo(message.chat.id, photo=img, caption=result)
            with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                    photo_1[0]), "rb") as img:
                bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id='@coin_minsk',
                                       message_id=msg_id)  # обновляем сообщение


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, )
    print(call.data.split(':'))
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
        print(call.data.split(':'))
        current_lot_id = call.data.split(':')[2]
        current_datetime = DT.datetime.now()
        with conn:
            start_time1 = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            end_time2 = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
        start_time = datetime.strptime(str(current_datetime)[:19], "%Y-%m-%d %H:%M:%S")  # 2021-10-01 12:00:00
        end_time = datetime.strptime(end_time2[0][:19], "%Y-%m-%d %H:%M:%S")
        timedelta = pd.Timestamp(end_time) - pd.Timestamp(start_time)
        if start_time < end_time:
            bot.answer_callback_query(call.id, f"Осталось времени: "
                                               f"{timedelta.components.days} дней "
                                               f"{timedelta.components.hours} часов "
                                               f"{timedelta.components.minutes} минут "
                                               f"{timedelta.components.seconds} секунд", show_alert=False)
        else:
            bot.answer_callback_query(call.id, f"Время истекло", show_alert=False)


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
    if call.data.split(':')[1] == "my_auc":
        print("Отправляем текст c info юзера по аукционам")
        user_telegram_id = call.message.chat.id
        try:
            with conn:
                trade_info_lst = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE trades_status = 'finished'")]
        except Exception as e:
            print(e)
        print(trade_info_lst)
        result = ""
        for info in trade_info_lst:
            trade_info = json.loads(info)
            if str(user_telegram_id) in trade_info:
                trade_number = trade_info_lst.index(info) + 1
                max_user_bid = trade_info[str(user_telegram_id)][1]
                number_of_bids = trade_info["bid_history"].count(user_telegram_id)
                try:
                    with conn:
                        lot_id = [i[1] for i in conn.execute(f"SELECT * FROM Trades WHERE id = {trade_number}")][0]
                        lot_name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")][0]
                        max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {trade_number}")][0]
                except Exception as e:
                    print(e)
                if user_telegram_id in trade_info["bid_history"] and trade_info["bid_history"][-1] == user_telegram_id:
                    result += f"Лот {trade_number}: {lot_name} - выигран. Сделано ставок: {number_of_bids}. " \
                              f"Выигрышная ставка: {max_price} руб.\n"
                if user_telegram_id in trade_info["bid_history"] and trade_info["bid_history"][-1] != user_telegram_id:
                    result += f"Лот {trade_number}: {lot_name} -  не выигран. Сделано ставок: {number_of_bids}. " \
                              f"Максимальная ставка: {max_user_bid} руб.\n"

        if len(result) > 0:
            result = "Вы приняли участие в торгах по следующим лотам:\n" + result
        else:
            result = "Вы еще не принимали участие в торгах либо торги по лоту еще не завершились\n"
        print(result)
        bot.edit_message_text(f"{result}",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    if call.data.split(':')[1] == "lottery":
        print("Отправляем текст c правилами начисления баллов")
        bot.edit_message_text("‼️Внимание Розыгрыш‼️\n"
                              "Общий призовой фонд 66000₽🔥\n"
                              "Конкурс рассчитан на Вашу активность, за каждую ставку и выигранный лот на аукционе "
                              "@coin_minsk Вам будут начисляться бонусные баллы:\n\n"
                              "Победная ставка|      Кол-во баллов|\n"
                              "0 - 249₽                  |      1️⃣0️⃣ баллов\n"
                              "250 - 499₽             |      2️⃣0️⃣ баллов\n"
                              "500 - 999₽             |      3️⃣0️⃣ баллов\n"
                              "1000 - 1999₽        |      5️⃣0️⃣ баллов\n"
                              "2000 - 4999₽        |      1️⃣5️⃣0️⃣ баллов\n"
                              "5000 - 9999₽        |      3️⃣0️⃣0️⃣ баллов\n"
                              "от 10000₽             |      5️⃣0️⃣0️⃣ баллов\n"
                              "от 20000₽             |      1️⃣0️⃣0️⃣0️⃣баллов\n"
                              "от 30000₽             |      2️⃣0️⃣0️⃣0️⃣баллов\n"
                              "Обычная ставка  |     3️⃣ балла\n\n"
                              "Подсчёт баллов производится каждый день после окончания аукциона, бот автоматически "
                              "вносит изменения в таблицу участников. Контролировать бонусные балы можно "
                              "самостоятельно в личном кабинете бота по команде.\n"
                              "Дата проведения 25.09.23 - 31.12.23\n"
                              "Итоги подведём 31 Декабря.\n\n"
                              "\U0001F3C6ГЛАВНЫЙ ПРИЗ - Трояк 1597. Вильно, Сигизмунд Ваза. Дата сверху - RRRR! Родная,"
                              "многолетняя патина! 7500 рублей!\n"
                              "\U0001F9482 Место - Грош 1546. Вильно, Сигизмунд Август\n"
                              "\U0001F9493 Место - Грош 1528. Краков, Сигизмунд Старый\n"
                              "4 Место - Двойной денарий 1567 г. Сигизмунд II Август, ВКЛ\n"
                              "5 Место - 2 марки 1906г.Вюртемберг\n"
                              "6 Место - Медный солид / Боратинка 1666г. Ян II Казимир Ваза\n"
                              "7 Место - 8 грошей 1772. Варшава, Станислав Понятовский. Год пореже!\n"
                              "8 Место - Орт 1622. Быдгощ, Сигизмунд Ваза\n"
                              "9 Место - 1 Флорин 1886г\n"
                              "10 Место - 5 Марок Третий Рейх\n"
                              "11 Место - Трояк 1601. Краков, Сигизмунд Ваза\n"
                              "12 Место - Денарий 1546. Вильно, Сигизмунд Август. Редкий!\n"
                              "Удачных торгов и выгодных покупок!.",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    if call.data.split(':')[1] == "top":
        print("Отправляем текст c top юзерами по количеству баллов")
        top_users_lst = [f"{i[0][:3] if len(i[0]) >= 3 else i[0][:1]} | Баллов: {i[1]}\n" for i in
                         conn.execute(f"SELECT DISTINCT full_name, try_strike FROM Clients ORDER BY try_strike DESC")]
        print(top_users_lst)
        result = f""
        num = 1
        if len(top_users_lst) > 12:
            for user in top_users_lst:
                result += f"{num}) {user}"
                num += 1
        else:
            for user in top_users_lst[:]:
                result += f"{num}) {user}"
                num += 1
        print(result)
        bot.edit_message_text(f"{result}",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    if call.data.split(':')[1] == "stats":
        print("Отправляем текст cо статистикой участия юзера в аукционах")
        user_telegram_id = call.message.chat.id
        try:
            with conn:
                trade_info_lst = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE trades_status = 'finished'")]
        except Exception as e:
            print(e)
        print(trade_info_lst)
        result = ""
        for info in trade_info_lst:
            trade_info = json.loads(info)
            if str(user_telegram_id) in trade_info:
                trade_number = trade_info_lst.index(info) + 1
                max_user_bid = trade_info[str(user_telegram_id)][1]
                number_of_bids = trade_info["bid_history"].count(user_telegram_id)
                try:
                    with conn:
                        lot_id = [i[1] for i in conn.execute(f"SELECT * FROM Trades WHERE id = {trade_number}")][0]
                        lot_name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {lot_id}")][0]
                        max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {trade_number}")][0]
                except Exception as e:
                    print(e)
                if user_telegram_id in trade_info["bid_history"] and trade_info["bid_history"][-1] == user_telegram_id:
                    result += f"Лот {trade_number}: {lot_name} - выигран. Сделано ставок: {number_of_bids}. " \
                              f"Выигрышная ставка: {max_price} руб.\n"
                if user_telegram_id in trade_info["bid_history"] and trade_info["bid_history"][-1] != user_telegram_id:
                    result += f"Лот {trade_number}: {lot_name} -  не выигран. Сделано ставок: {number_of_bids}. " \
                              f"Максимальная ставка: {max_user_bid} руб.\n"

        if len(result) > 0:
            result = "Вы приняли участие в торгах по следующим лотам:\n" + result
        else:
            result = "Вы еще не принимали участие в торгах либо торги по лоту еще не завершились\n"
        print(result)
        bot.edit_message_text(f"{result}",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=create_universal_inline_keyb(Return_to_menu_keyb_dct))
    if call.data.split(':')[0] == "bid":
        current_bid = int(call.data.split(':')[1])
        current_lot_id = call.data.split(':')[2]
        print("ставка", current_bid)
        print("лот", current_lot_id)
        try:
            with conn:
                # Получаем JSON-строку
                trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][
                    0]
        except Exception as e:
            print(e)
        trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
        print("Инфа по торгам", trade_info)
        last_bid_id = trade_info["bid_history"][-1]
        print("-0- Юзер с последней ставкой", last_bid_id, type(last_bid_id))
        # Добавляем данные по торгам и ставке клиента в объект (словарь)
        # user_telegram_id = call.message.from_user.id
        user_telegram_id = call.message.chat.id
        # user_telegram_username = call.message.from_user.username
        # user_first_name = call.message.from_user.first_name
        # user_last_name = call.message.from_user.last_name
        print("айди юзера", user_telegram_id)

        with conn:
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
        current_datetime = DT.datetime.now()
        if datetime.strptime(str(current_datetime)[:19], "%Y-%m-%d %H:%M:%S") < datetime.strptime(end_time[0][:19],
                                                                                                  "%Y-%m-%d %H:%M:%S"):
            print("аук еще продолжается, можно делать ставки")
            if str(user_telegram_id) not in trade_info:
                print("раньше не делал ставку")
                print("-1- Юзер с последеней ставкой", last_bid_id, type(last_bid_id))
                max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                        f"{current_lot_id}")][0] + current_bid
                trade_info[str(user_telegram_id)] = [current_bid, max_price]  # записываем юзера и ставку в словарь в список
                trade_info["bid_history"].append(user_telegram_id)
                trade_info_str = json.dumps(trade_info)  # Преобразуем объект обратно в строку для записи в БД


                with conn:
                    conn.execute("UPDATE Trades SET trade_info = ? WHERE lots_id = ?",
                                 (trade_info_str, current_lot_id))  # обновляем информацию по торгу "Trades"
                    conn.execute("UPDATE Trades SET max_price = ? WHERE lots_id = ?",
                                 (max_price, current_lot_id))  # обновляем цену лота в "Trades"
                    conn.execute("UPDATE Clients SET try_strike = ? WHERE telegram_id = ?",
                                 (3, user_telegram_id))
                conn.commit()


                with conn:
                    name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                try:
                    with conn:
                        # Получаем JSON-строку
                        trade_info_str = \
                        [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
                except Exception as e:
                    print(e)
                bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                sorted_bids_dct = sorted(bids_dct.items(), key=lambda x: x[1][1], reverse=True)
                print(sorted_bids_dct)
                top_bids = ""  # список топовых участников аукциона
                medal_places = ['\U0001F947', '\U0001F948', '\U0001F949']  # эмоджи медалек: голд, силвер, бронз
                if 0 < len(sorted_bids_dct) < 4:
                    for i in range(1, len(sorted_bids_dct)):
                        print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                        with conn:
                            auc_participant_name = [i[1] for i in conn.execute(
                                f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                        if len(auc_participant_name) > 3:
                            auc_participant_name = f"{auc_participant_name[:3]}***"
                        else:
                            auc_participant_name = f"{auc_participant_name[:1]}***"
                        top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                else:
                    for i in range(1, 4):
                        print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                        with conn:
                            auc_participant_name = [i[1] for i in conn.execute(
                                f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                        if len(auc_participant_name) > 3:
                            auc_participant_name = f"{auc_participant_name[:3]}***"
                        else:
                            auc_participant_name = f"{auc_participant_name[:1]}***"
                        top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"

                result = f"Номер лота: {current_lot_id}\n" \
                         f"Название лота: {name[0]}\n" \
                         f"Описание: {description[0]}\n" \
                         f"Расположение продавца: {geolocations[0]}\n" \
                         f"Продавец: {link_seller[0]}\n" \
                         f"Ваша последняя ставка: {current_bid} руб.\n" \
                         f"Текущая цена аукциона: {max_price} руб.\n\n" \
                         f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                         f"{top_bids}"
                print(result)
                with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                        photo_1[0]), "rb") as img:
                    bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                           message_id=call.message.message_id,
                                           reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct,
                                                                                 current_lot_id))  # обновляем сообщение с клавиатурой
                msg = bot.send_message(call.message.chat.id, f"Ваша ставка на {current_bid} руб. принята.")
                time.sleep(3)
                bot.delete_message(call.message.chat.id, msg.message_id)
            else:
                try:
                    with conn:
                        # Получаем JSON-строку
                        trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                     f"{current_lot_id}")][0]
                except Exception as e:
                    print(e)
                trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                print("Инфа по торгам", trade_info)
                last_bid_id = trade_info["bid_history"][-1]
                print("-0- Юзер с последеней ставкой", last_bid_id, type(last_bid_id))
                if user_telegram_id != last_bid_id:
                    print("раньше делал ставку, но ее перебили", user_telegram_id, )
                    print("-2- Юзер с последней ставкой", last_bid_id, type(last_bid_id))
                    max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                            f"{current_lot_id}")][0] + current_bid
                    trade_info[str(user_telegram_id)] = [current_bid, max_price]
                    trade_info["bid_history"].append(user_telegram_id)
                    trade_info_str = json.dumps(trade_info)  # Преобразуем объект обратно в строку
                    with conn:
                        conn.execute("UPDATE Trades SET trade_info = ? WHERE lots_id = ?",
                                     (trade_info_str, current_lot_id))  # добавьте новую запись в таблицу "Trades"
                        conn.execute("UPDATE Trades SET max_price = ? WHERE lots_id = ?",
                                     (max_price, current_lot_id))  # добавьте новую запись в таблицу "Trades"
                        conn.execute("UPDATE Clients SET try_strike = ? WHERE telegram_id = ?",
                                     (3, user_telegram_id))
                    conn.commit()
                    with conn:
                        name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    try:
                        with conn:
                            # Получаем JSON-строку
                            trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                         f"{current_lot_id}")][0]
                    except Exception as e:
                        print(e)
                    bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                    sorted_bids_dct = sorted(bids_dct.items(), key=lambda x: x[1][1], reverse=True)
                    print("-2- Выборка топовых участников", sorted_bids_dct)
                    top_bids = ""  # список топовых участников аукциона
                    medal_places = ['\U0001F947', '\U0001F948', '\U0001F949']  # эмоджи медалек голд силвер бронз
                    if 0 < len(sorted_bids_dct) < 4:
                        for i in range(1, len(sorted_bids_dct)):
                            print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                            with conn:
                                auc_participant_name = [i[1] for i in conn.execute(
                                    f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                            if len(auc_participant_name) > 3:
                                auc_participant_name = f"{auc_participant_name[:3]}***"
                            else:
                                auc_participant_name = f"{auc_participant_name[:1]}***"
                            top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                    else:
                        for i in range(1, 4):
                            print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                            with conn:
                                auc_participant_name = [i[1] for i in conn.execute(
                                    f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                            if len(auc_participant_name) > 3:
                                auc_participant_name = f"{auc_participant_name[:3]}***"
                            else:
                                auc_participant_name = f"{auc_participant_name[:1]}***"
                            top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                    result = f"Номер лота: {current_lot_id}\n" \
                             f"Название лота: {name[0]}\n" \
                             f"Описание: {description[0]}\n" \
                             f"Расположение продавца: {geolocations[0]}\n" \
                             f"Продавец: {link_seller[0]}\n" \
                             f"Ваша последняя ставка: {current_bid} руб.\n" \
                             f"Текущая цена аукциона: {max_price} руб.\n\n" \
                             f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                             f"{top_bids}"
                    print(result)
                    with open(
                            r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                                    photo_1[0]), "rb") as img:
                        bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                               message_id=call.message.message_id,
                                               reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct,
                                                                                     current_lot_id))  # обновляем сообщение с клавиатурой
                    msg = bot.send_message(call.message.chat.id, f"Ваша ставка на {current_bid} руб. принята")
                    time.sleep(3)
                    bot.delete_message(call.message.chat.id, msg.message_id)

                if user_telegram_id == last_bid_id:
                    print("раньше делал ставку, и она последняя, т.е. ее не перебивали")
                    print("-3- Юзер с последеней ставкой", last_bid_id, type(last_bid_id))
                    current_bid = int(call.data.split(':')[1])
                    current_lot_id = call.data.split(':')[2]
                    try:
                        with conn:
                            # Получаем JSON-строку
                            trade_info_str = \
                            [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
                    except Exception as e:
                        print(e)
                    trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                    # Добавляем данные по торгам и ставке клиента в объект (словарь)
                    user_telegram_id = call.message.from_user.id
                    user_telegram_id = call.message.chat.id
                    user_telegram_username = call.message.from_user.username
                    user_first_name = call.message.from_user.first_name
                    user_last_name = call.message.from_user.last_name
                    print(user_telegram_id)
                    max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                            f"{current_lot_id}")][0]
                    with conn:
                        name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                        end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    try:
                        with conn:
                            trade_info_str = \
                                [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
                    except Exception as e:
                        print(e)
                    bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                    sorted_bids_dct = sorted(bids_dct.items(), key=lambda x: x[1][1], reverse=True)
                    print(sorted_bids_dct)
                    top_bids = ""  # список топовых участников аукциона
                    medal_places = ['\U0001F947', '\U0001F948', '\U0001F949']  # эмоджи медалек голд силвер бронз
                    if 0 < len(sorted_bids_dct) < 4:
                        for i in range(1, len(sorted_bids_dct)):
                            print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                            with conn:
                                auc_participant_name = [i[1] for i in conn.execute(
                                    f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                            if len(auc_participant_name) > 3:
                                auc_participant_name = f"{auc_participant_name[:3]}***"
                            else:
                                auc_participant_name = f"{auc_participant_name[:1]}***"
                            top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                    else:
                        for i in range(1, 4):
                            print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                            with conn:
                                auc_participant_name = [i[1] for i in conn.execute(
                                    f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][0]
                            if len(auc_participant_name) > 3:
                                auc_participant_name = f"{auc_participant_name[:3]}***"
                            else:
                                auc_participant_name = f"{auc_participant_name[:1]}***"
                            top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                    current_bid_datetime = DT.datetime.now()
                    result = f"Номер лота: {current_lot_id}\n" \
                             f"Название лота: {name[0]}\n" \
                             f"Описание: {description[0]}\n" \
                             f"Расположение продавца: {geolocations[0]}\n" \
                             f"Продавец: {link_seller[0]}\n" \
                             f"Текущая цена аукциона: {max_price} руб.\n\n" \
                             f"Ваша ставка на {current_bid} руб. в {str(current_bid_datetime)[:19]} не принята.\n" \
                             f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                             f"{top_bids}"
                    print(result)
                    with open(
                            r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                                    photo_1[0]), "rb") as img:
                        bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                               message_id=call.message.message_id,
                                               reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct,
                                                                                     current_lot_id))  # обновляем сообщение с клавиатурой
                    msg = bot.send_message(call.message.chat.id, f"Ваша предыдущая ставка последняя, ставка на "
                                                                 f"{current_bid} руб. не принята. Cледите за аукционом, "
                                                                 f"обновляйте карточку лота с помощью кнопки 'Обновить'")
                    time.sleep(3)
                    bot.delete_message(call.message.chat.id, msg.message_id)
        else:
            print("аук завершен")
            with conn:
                max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
                name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            result = f"Номер лота: {current_lot_id}\n" \
                     f"Название лота: {name[0]}\n" \
                     f"Описание: {description[0]}\n" \
                     f"Расположение продавца: {geolocations[0]}\n" \
                     f"Продавец: {link_seller[0]}\n" \
                     f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                     f"\U0001F3C1Аукцион завершен.\n"
            try:
                with conn:
                    trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                 f"{current_lot_id}")][0]
            except Exception as e:
                print(e)
            trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
            msg_id = trade_info["bid_history"][0]
            if len(trade_info["bid_history"]) > 1:
                winner_id = trade_info["bid_history"][-1]
                point_dct = {10: [0, 249], 20: [250, 499], 30: [500, 999], 50: [1000, 1999], 150: [2000, 4999],
                             300: [5000, 9999], 500: [10000, 19999], 1000: [20000, 29999], 2000: [30000, 100000000]}
                point = [i[5] for i in conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {winner_id}")][0]
                for key, value in point_dct.items():
                    if value[0] <= max_price <= value[1]:
                        point += key
                with conn:
                    winner_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {winner_id}")][0]
                    conn.execute("UPDATE Clients SET try_strike = ? WHERE telegram_id = ?",
                                 (point, winner_id))
                    conn.execute("UPDATE Trades SET trades_status = ? WHERE lots_id = ?",
                                 ("finished", current_lot_id))  # добавьте новую запись в таблицу "Trades"
                    result += f"\U0001F3C6Победитель: {winner_name} (Финальная цена: {max_price} руб.)"
            else:
                winner_name = "Победителей нет."
                result += winner_name
            with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                    photo_1[0]), "rb") as img:
                bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)  # обновляем сообщение
            with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                    photo_1[0]), "rb") as img:
                bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id='@coin_minsk',
                                       message_id=msg_id)  # обновляем сообщение


    if call.data.split(':')[1] == "update_auction":
        current_lot_id = call.data.split(':')[2]
        try:
            with conn:
                # Получаем JSON-строку
                trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                             f"{current_lot_id}")][0]
        except Exception as e:
            print(e)
        trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
        count_bid = len(trade_info["bid_history"])
        last_bid = trade_info["bid_history"][-1]
        # Добавляем данные по торгам и ставке клиента в объект (словарь)
        user_telegram_id = call.message.from_user.id
        user_telegram_id = call.message.chat.id
        user_telegram_username = call.message.from_user.username
        user_first_name = call.message.from_user.first_name
        user_last_name = call.message.from_user.last_name
        print(user_telegram_id)
        max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
        with conn:
            name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
            end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
        try:
            with conn:
                trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][
                    0]
        except Exception as e:
            print(e)
        bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
        sorted_bids_dct = sorted(bids_dct.items(), key=lambda x: x[1][1], reverse=True)
        print(sorted_bids_dct)
        top_bids = ""  # список топовых участников аукциона
        medal_places = ['\U0001F947', '\U0001F948', '\U0001F949']  # эмоджи медалек голд силвер бронз
        if 0 < len(sorted_bids_dct) < 4:
            for i in range(1, len(sorted_bids_dct)):
                print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                with conn:
                    auc_participant_name = \
                        [i[1] for i in
                         conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][
                            0]
                if len(auc_participant_name) > 3:
                    auc_participant_name = f"{auc_participant_name[:3]}***"
                else:
                    auc_participant_name = f"{auc_participant_name[:1]}***"
                top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
        else:
            for i in range(1, 4):
                print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                with conn:
                    auc_participant_name = \
                        [i[1] for i in
                         conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][
                            0]
                if len(auc_participant_name) > 3:
                    auc_participant_name = f"{auc_participant_name[:3]}***"
                else:
                    auc_participant_name = f"{auc_participant_name[:1]}***"
                top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
        current_update_datetime = DT.datetime.now()
        result = f"Номер лота: {current_lot_id}\n" \
                 f"Название лота: {name[0]}\n" \
                 f"Описание: {description[0]}\n" \
                 f"Расположение продавца: {geolocations[0]}\n" \
                 f"Продавец: {link_seller[0]}\n" \
                 f"Текущая цена аукциона: {max_price} руб.\n\n" \
                 f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                 f"{top_bids}\n" \
                 f"Дата и время обновления: {str(current_update_datetime)[:19]}"
        print(result)
        with open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                photo_1[0]), "rb") as img:
            bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct,
                                                                         current_lot_id))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Данные лота номер {current_lot_id}: {name[0]} обновлены.\n"
                                                     f"Дата и время обновления: {str(current_update_datetime)[:19]}\n"
                                                     f"Следите за ставками, делайте Ваши ставки!")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)

        """__________________________________________________________________________________________________________"""
        for i in range(10):  # цикл для мониторинга базы данных
            if check_db(current_lot_id, count_bid, last_bid, user_telegram_id):  # Проверяем, есть ли изменения в базе данных
                print("изменения есть, кто-то сделал ставку")
                # Если есть, то обновляем карточку и отправляем сообщение
                try:
                    with conn:
                        trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                     f"{current_lot_id}")][0]
                except Exception as e:
                    print(e)
                trade_info = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                # Добавляем данные по торгам и ставке клиента в объект (словарь)
                max_price = [i[4] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = {current_lot_id}")][0]
                with conn:
                    name = [i[1] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    description = [i[2] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    start_price = [i[3] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    link_seller = [i[4] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    photo_1 = [i[5] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    geolocations = [i[6] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    start_time = [i[7] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                    end_time = [i[8] for i in conn.execute(f"SELECT * FROM Lots WHERE id = {current_lot_id}")]
                try:
                    with conn:
                        trade_info_str = [i[2] for i in conn.execute(f"SELECT * FROM Trades WHERE lots_id = "
                                                                     f"{current_lot_id}")][0]
                except Exception as e:
                    print(e)
                bids_dct = json.loads(trade_info_str)  # Преобразуем JSON-строку в объект
                sorted_bids_dct = sorted(bids_dct.items(), key=lambda x: x[1][1], reverse=True)
                print(sorted_bids_dct)
                top_bids = ""  # список топовых участников аукциона
                medal_places = ['\U0001F947', '\U0001F948', '\U0001F949']  # эмоджи медалек голд силвер бронз
                if 0 < len(sorted_bids_dct) < 4:
                    for i in range(1, len(sorted_bids_dct)):
                        print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                        with conn:
                            auc_participant_name = \
                                [i[1] for i in
                                 conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][
                                    0]
                        if len(auc_participant_name) > 3:
                            auc_participant_name = f"{auc_participant_name[:3]}***"
                        else:
                            auc_participant_name = f"{auc_participant_name[:1]}***"
                        top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                else:
                    for i in range(1, 4):
                        print(f"{sorted_bids_dct[i][0]}: {sorted_bids_dct[i][1][1]}")
                        with conn:
                            auc_participant_name = \
                                [i[1] for i in
                                 conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {sorted_bids_dct[i][0]}")][
                                    0]
                        if len(auc_participant_name) > 3:
                            auc_participant_name = f"{auc_participant_name[:3]}***"
                        else:
                            auc_participant_name = f"{auc_participant_name[:1]}***"
                        top_bids += f"{medal_places[i - 1]}{sorted_bids_dct[i][1][1]}BYN({auc_participant_name})\n"
                current_update_datetime = DT.datetime.now()
                result = f"Номер лота: {current_lot_id}\n" \
                         f"Название лота: {name[0]}\n" \
                         f"Описание: {description[0]}\n" \
                         f"Расположение продавца: {geolocations[0]}\n" \
                         f"Продавец: {link_seller[0]}\n" \
                         f"Текущая цена аукциона: {max_price} руб.\n\n" \
                         f"\U0001F4B0Стартовая цена: {start_price[0]} руб.\n" \
                         f"{top_bids}\n" \
                         f"Дата и время обновления: {str(current_update_datetime)[:19]}"
                with open(
                        r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(
                                photo_1[0]), "rb") as img:
                    bot.edit_message_media(media=InputMediaPhoto(img, caption=result), chat_id=call.message.chat.id,
                                           message_id=call.message.message_id,
                                           reply_markup=create_trade_inline_keyb(Trade_inline_keyb_dct, current_lot_id))
                msg = bot.send_message(call.message.chat.id, f"Сделана новая ставка!"
                                                             f"Данные лота номер {current_lot_id}: {name[0]} обновлены.\n"
                                                             f"Дата и время обновления: {str(current_update_datetime)[:19]}\n"
                                                             f"Следите за ставками, делайте Ваши ставки!")
                time.sleep(5)
                bot.delete_message(call.message.chat.id, msg.message_id)
            time.sleep(5)  # Ждем х секунд перед следующей проверкой
        """__________________________________________________________________________________________________________"""


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
