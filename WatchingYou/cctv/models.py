# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    isSuperUser = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Image(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to='images/')

@receiver(pre_delete, sender=Image)
def mymodel_delete(sender, instance, **kwargs):
    instance.img.delete(False)