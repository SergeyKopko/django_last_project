from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import SET_NULL
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Clients(models.Model):
    fullname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    wallet = models.BigIntegerField()
    try_strike = models.IntegerField()

class Administration(AbstractUser, models.Model):

    username = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cleaned_data = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



class Lots(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_price = models.IntegerField()
    link_seller = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    geolocations = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
class Accept_lot(models.Model):
    admin_id = models.ForeignKey(Administration, on_delete=models.CASCADE, null=True)
    accept_status = models.CharField(max_length=100)
    lots_id = models.ForeignKey(Lots, on_delete=models.CASCADE, null=True)


class Traids(models.Model):
    lots = models.ForeignKey(Lots, on_delete=models.CASCADE, null=True)
    trade_info = models.TextField()
    traids_status = models.CharField(max_length=50)