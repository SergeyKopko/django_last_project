from django.urls import path

from .views import *

urlpatterns = [
    path('', main_window, name='home'),
    path('auction_cabinet', auction_cabinet, name='auction_cabinet')
]