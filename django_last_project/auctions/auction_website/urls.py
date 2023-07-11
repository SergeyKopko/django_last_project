from django.urls import path

from .views import *
urlpatterns = [
    path('', main_window, name='home'),
    path('login', loginAdmin, name='login'),
    path('register', registerAdmin.as_view(), name='register'),
    path('cabinet', cabinetAdministration, name='cabinet'),
    path('create_lots', createLots, name='create_lots'),
    path('acceptlots', AcceptLots, name='acceptlots'),
    path('infolot', infoAboutLot, name='infolot')

]