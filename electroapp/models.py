from django.db import models
from django.contrib.auth.models import *
import datetime,os
# Create your models here.


def get_file_path(instance, filename):
        name, file_extention = os.path.splitext(filename)
        now = datetime.datetime.now()
        cat=now.strftime("%Y_%m_%d_%H:%M:%S")
        name = '{}_{}{}'.format(cat, name, file_extention)
        return "products/{}".format(name)

class Product(models.Model):
    pname   =  models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    price = models.CharField(max_length=255, null=True)
    qty = models.CharField(max_length=255, null=True)
    image = models.FileField(upload_to=get_file_path ,null=True)
    created_at = models.DateTimeField(max_length=255,null=True)
    updated_at = models.DateTimeField(max_length=255, null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name='auth_user1',null=True)
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name='auth_user2',null=True)


class Order(models.Model):
<<<<<<< HEAD
    pdetail  =  models.JSONField(max_length=255, null=True)
    total  =  models.CharField(max_length=255, null=True)
=======
    pname   =  models.CharField(max_length=255, null=True)
    price = models.CharField(max_length=255, null=True)
    qty = models.CharField(max_length=255, null=True)
>>>>>>> 56d8bfa082b1df55c6196d413401794aecaf9946
    created_at = models.DateTimeField(max_length=255,null=True)
    updated_at = models.DateTimeField(max_length=255, null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name='auth_user3',null=True)
