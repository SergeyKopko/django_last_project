import sqlite3
from pathlib import Path
import json
import telebot
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import F
from telebot import types
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from .models import Administration, Accept_lot, Lots
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import UserCreationForm, LoginForm, CabinetForm, CreateLotsForm

conn = sqlite3.connect(r'C:\Users\voyag\PycharmProjects\django_last_project\telegram\auctions.db', check_same_thread=False)
# conn = sqlite3.connect('/django_last_project/telegram/auctions.db', check_same_thread=False)


def send_message_to_bot(name, description, start_price, geolocations, link_seller, photo, callback_Lots_id):
    print('Отработала')
    bot_token = '6112420224:AAF0gLi1ZFYabFDubwjawFyjDMjmtJ0_JZc'
    bot = telebot.TeleBot(token=bot_token)
    result = f"Название лота: {name}\n" \
             f"Описание: {description}\n" \
             f"Стартовая цена: {start_price} руб.\n" \
             f"Расположение продавца: {geolocations}\n" \
             f"Ссылка на продавца: {link_seller}\n"
    print(callback_Lots_id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Участвовать", url=f"https://t.me/Sun2307_bot?start={callback_Lots_id}"))
    keyboard.add(InlineKeyboardButton("\U0001F552", callback_data=f"view:timeleft:{callback_Lots_id}"),
                 InlineKeyboardButton("\U00002139", callback_data="view:info"))
    photos = open(r'C:/Users/voyag/PycharmProjects/django_last_project/django_last_project/auctions/media/' + str(photo), 'rb')
    message = bot.send_photo(chat_id='@coin_minsk', photo=photos, caption=result, reply_markup=keyboard)
    message_id = message.message_id
    trade_info = {"bid_history": [message_id]}
    trade_info_str = json.dumps(trade_info)
    trades_status = 'in progress'
    with conn:
        conn.execute("INSERT OR IGNORE INTO Trades (lots_id, trade_info, trades_status, max_price) "
                     "VALUES (?, ?, ?, ?)",
                     (callback_Lots_id, trade_info_str, trades_status, start_price))  # новая запись в таблицу "Trades"
    conn.commit()  # сохраняем изменения в базе данных


def main_window(request):
    return render(request, 'auction_website/home.html')
# Create your views here.

class registerAdmin(View):
    template_name = 'registration/register.html'

    def get(self, request):


        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context=context)
    def post(self, request):
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                user = authenticate(email=email, password=password)
                login(request, user)
                return redirect('home')
            context = {
                'form':form
            }
            return render(request, self.template_name, context)





def loginAdmin(request):
    link_address = 'registration/login.html'
    form = LoginForm()
    contenxt = {
        'form': form
    }
    return redirect(request, link_address, contenxt= contenxt)


def cabinetAdministration(request):
    link_address = 'auction_website/cabinet.html'
    form = CabinetForm()
    context = {
        'form': form,
    }
    if request.method == 'POST':
        form = CabinetForm(request.POST)
        # print(form)
        if form.is_valid():
            phone = request.POST.get('phone')
            address = request.POST.get('address')

            Administration.objects.filter(pk=request.user.id).update(address=address)
            Administration.objects.filter(pk=request.user.id).update(phone=phone)

            return redirect("cabinet")
            # Administration.objects.filter(username=request.user.username).update(phone = Administration.phone+str(phone), address=Administration.address+str(address))\
        if 'update' in request.POST:

            # print(list(request.POST.values()))
            Administration.objects.filter(pk=request.user.id).update(address="")
            Administration.objects.filter(pk=request.user.id).update(phone="")




            return redirect("cabinet")

    return render(request, link_address, context=context)

def createLots(request):
    link_address = 'auction_website/create_lots.html'
    if request.method == 'POST':
        form = CreateLotsForm(request.POST, request.FILES)
        # print('Данные валидные - ПРОВЕРКА')
        if form.is_valid():
            form.save()

            lots_id = Lots.objects.last()
            name_lot_in_db_telegram = lots_id.name
            descriptions_lot_in_db_telegram = lots_id.description
            start_price_lot_in_db_telegram = lots_id.start_price
            link_seller_lot_in_db_telegram = lots_id.link_seller
            geolocations_lot_in_db_telegram = lots_id.geolocations
            start_time_lot_in_db_telegram = lots_id.start_time
            end_time_lot_in_db_telegram = lots_id.end_time
            photo_lot_in_db_telegram = lots_id.photo
            print(end_time_lot_in_db_telegram, ' ----', start_time_lot_in_db_telegram)
            lots_table = "INSERT OR IGNORE INTO Lots (name, descriptions, start_price, link_seller, geolocations,start_time, end_time, photo) values(?, ?, ?, ?, ?, ?, ?, ?)"
            admin_id_lot_in_db_telegram = Administration.objects.last().id
            lots_id_lot_in_db_telegram = lots_id.id
            acceptlots_table = "INSERT OR IGNORE INTO Accept_lot (admin_id, lots_id, accept_status) values(?, ?, ?)"
            with conn:
                conn.execute(lots_table, [name_lot_in_db_telegram, descriptions_lot_in_db_telegram, start_price_lot_in_db_telegram, link_seller_lot_in_db_telegram, geolocations_lot_in_db_telegram, start_time_lot_in_db_telegram, end_time_lot_in_db_telegram, str(photo_lot_in_db_telegram)])
                conn.execute(acceptlots_table, [admin_id_lot_in_db_telegram, lots_id_lot_in_db_telegram, 'in_progress'])
            Accept_lot.objects.create(admin_id = Administration.objects.last(), lots_id = lots_id, accept_status = 'in_progress')
            # print(Accept_lot.objects.all())
            return redirect('create_lots')


    form = CreateLotsForm()

    context = {
        'form':form
    }

    return render(request, link_address, context=context)
def AcceptLots(request):
    link_address = 'auction_website/acceptlots.html'
    lots = Lots.objects.all()
    form = Accept_lot.objects.all()
    lots_list = []
    for i in form:
        for j in lots:
            if i.lots_id == j:
                lots_list.append(j)
    if request.method == 'POST':
        check_this_id_with_id_acceptlotslots_id = list(request.POST.values())[1]
        form_in_confirmed = Accept_lot.objects.filter(lots_id = check_this_id_with_id_acceptlotslots_id)
        lots_id_from_acceptlot = form_in_confirmed[0].lots_id
        info_about_lot_request_telegram = [lots_id_from_acceptlot.name,lots_id_from_acceptlot.description,lots_id_from_acceptlot.start_price, lots_id_from_acceptlot.link_seller, lots_id_from_acceptlot.geolocations, lots_id_from_acceptlot.photo, lots_id_from_acceptlot.id]
        # print(info_about_lot_request_telegram[5])
        form_in_confirmed.update(accept_status = 'confirmed')
        with conn:
            conn.execute('UPDATE Accept_lot SET accept_status = ? WHERE lots_id = ?', ('confirmed', check_this_id_with_id_acceptlotslots_id))
        send_message_to_bot(info_about_lot_request_telegram[0], info_about_lot_request_telegram[1], info_about_lot_request_telegram[2], info_about_lot_request_telegram[4], info_about_lot_request_telegram[3], str(info_about_lot_request_telegram[5]), info_about_lot_request_telegram[6])
        return redirect('acceptlots')


    context = {
        'form_lots':lots_list,
        'form': form
    }
    return render(request, link_address, context=context)


def infoAboutLot(request):
    link_address = 'auction_website/infolot.html'
    acc_lot = Accept_lot.objects.filter(accept_status='confirmed')
    lot_id = [i.lots_id for i in acc_lot]
    list_lot_in_infolot = []
    for i in lot_id:
        lots = Lots.objects.filter(pk = i.id)
        print(lots)
        if lots:
            list_lot_in_infolot.append(lots)
    print(list_lot_in_infolot)
    context = {
        'form': list_lot_in_infolot
    }
    return render(request, link_address, context=context)



