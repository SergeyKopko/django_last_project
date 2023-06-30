from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, BaseUserCreationForm
from django.forms import EmailInput, TextInput, PasswordInput, ModelForm, NumberInput, FileInput, DateTimeInput, URLInput, Form

from .models import Administration, Lots

User = get_user_model()
class UserCreationForm(UserCreationForm, BaseUserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

        fields = ('email','username', 'password1', 'password2')

        widgets = {
            'email': EmailInput(attrs={
                'class':'',
                'placeholder':'Введите вашу почту'
            }),

            'username': TextInput(attrs={
                'class': '',
                'placeholder': 'Введите Ваше ФИО'
            }),
            'password1': PasswordInput(attrs={
                'class': '',
                'placeholder': 'Введите пароль'
            }),
            'password2': PasswordInput(attrs={
                'class': '',
                'placeholder': 'Введите пароль повторно'
            })
        }

class LoginForm(AuthenticationForm):
    pass

class CabinetForm(ModelForm):
    class Meta:
        model = User

        fields = ('phone', 'address', 'cleaned_data', 'username')

        widgets = {
            'phone': TextInput(attrs={
                'placeholder': 'Введите моб.телефон'
            }),
            'address': TextInput(attrs={
                'placeholder': 'Введите ваш адрес'
            }),
        }


class CreateLotsForm(ModelForm):
    class Meta:
        model = Lots
        fields = ('name', 'description', 'start_price', 'link_seller','photo', 'geolocations', 'start_time', 'end_time')
        widgets = {
            'name': TextInput(attrs={
                'placeholder': 'Введите название лота',
                'class':'create_info_form'
            }),
            'description': TextInput(attrs={
                'placeholder': 'Введите описание лота',
                'class': 'create_info_form'
            }),
            'link_seller': URLInput(attrs={
                'placeholder': 'Введите ссылку на продавца',
                'class': 'create_info_form'
            }),
            'start_price': TextInput(attrs={
                'placeholder': 'Введите начальную цену лота',
                'class': 'create_info_form'
            }),
            'photo': FileInput(attrs={
                'placeholder': 'Вставьте картинку продукта',
                'class': 'create_info_form'
            }),
            'geolocations': TextInput(attrs={
                'placeholder': 'Введите вашу геолокацию',
                'class': 'create_info_form'
            }),
            'start_time': DateTimeInput(attrs={
                'placeholder': 'Введите начало продаж',
                'class': 'create_info_form'
            }),
            'end_time': DateTimeInput(attrs={
                'placeholder': 'Введите время конца продаж',
                'class': 'create_info_form'
            }),
        }