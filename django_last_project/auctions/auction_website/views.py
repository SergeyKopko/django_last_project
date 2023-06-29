from django.http import HttpResponse
from .views import *


def main_window(request):
    return HttpResponse('Главная страница ВОТ ТАК')
# Create your views here.
def auction_cabinet(request):
    return HttpResponse('Кабинет пользователя')