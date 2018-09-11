# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    isSuperUser = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Image(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to='images/')

