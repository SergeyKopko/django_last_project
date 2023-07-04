import sqlite3
from pathlib import Path

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

def send_message_to_bot(name, description, start_price, geolocations, link_seller, photo):
    print('Отработала')
    bot_token = '5937676517:AAEG8U11wayyFFQmbJKi3Y3BdINCzUTIDWs'
    bot = telebot.TeleBot(token=bot_token)
    result = f"Название лота: {name}\n" \
             f"Описание: {description}\n" \
             f"Стартовая цена: {start_price} руб.\n" \
             f"Расположение продавца: {geolocations}\n" \
             f"Ссылка на продавца: {link_seller}\n"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Участвовать", callback_data='gfgf'))
    keyboard.add(InlineKeyboardButton("\U0001F552", callback_data="qwerty:timeleft"), InlineKeyboardButton("\U00002139", callback_data="qwerty:info"))
    photos = open(r'C:/Users/admin/django_last_project1/django_last_project/auctions/media/'+ str(photo), 'rb')
    bot.send_photo(chat_id='@coin_minsk', photo=photos, caption=result, reply_markup=keyboard)






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
        if form.is_valid():
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            Administration.objects.filter(username = request.user.username).update(phone = phone)
            Administration.objects.filter(username = request.user.username).update(address = address)
            return redirect("cabinet")
            # Administration.objects.filter(username=request.user.username).update(phone = Administration.phone+str(phone), address=Administration.address+str(address))
    else:
        pass
    return render(request, link_address, context=context)

def createLots(request):
    link_address = 'auction_website/create_lots.html'
    if request.method == 'POST':
        form = CreateLotsForm(request.POST, request.FILES)
        print('Данные валидные - ПРОВЕРКА')
        if form.is_valid():
            form.save()
            lots_id = Lots.objects.last()
            Accept_lot.objects.create(admin_id = Administration.objects.last(), lots_id = lots_id, accept_status = 'in_progress')
            # print(Accept_lot.objects.all())
            return redirect('home')

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
        a = list(request.POST.values())[1]
        form_in_confirmed = Accept_lot.objects.filter(lots_id = a)
        lots_id_from_acceptlot = form_in_confirmed[0].lots_id
        info_about_lot_request_telegram = [lots_id_from_acceptlot.name,lots_id_from_acceptlot.description,lots_id_from_acceptlot.start_price, lots_id_from_acceptlot.link_seller, lots_id_from_acceptlot.geolocations, lots_id_from_acceptlot.photo]
        print(info_about_lot_request_telegram[5])
        form_in_confirmed.update(accept_status = 'confirmed')

        send_message_to_bot(info_about_lot_request_telegram[0], info_about_lot_request_telegram[1], info_about_lot_request_telegram[2], info_about_lot_request_telegram[4], info_about_lot_request_telegram[3], str(info_about_lot_request_telegram[5]))
        return redirect('acceptlots')


    context = {
        'form_lots':lots_list,
        'form': form
    }

    conn = sqlite3.connect(r'C:\Users\admin\django_last_project1\telegram\auctions.db')
    with conn:
        f = [i for i in conn.execute('SELECT * FROM Lots')]



    return render(request, link_address, context=context)


