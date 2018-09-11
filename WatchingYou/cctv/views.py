# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.http import HttpResponse

import json

from .models import User, Image

from django.core.signing import Signer

signer = Signer()

def index(request):
    if not request.session.get('login_user_exists'):
        request.session['login_user_exists'] = True
    if not request.session.get('login_password_right'):
        request.session['login_password_right'] = True
    if request.session.get('login'):
        return redirect('/video/')
    context = {
        'user_exists': request.session['login_user_exists'],
        'password_right': request.session['login_password_right'],
    }
    return render(request, 'cctv/index.html', context)

def login_check(request):
    if request.method == 'POST':
        user = User.objects.filter(name=request.POST['user_name'])
        password = request.POST['user_password']
        if not user:
            request.session['login_user_exists'] = False
            return redirect('/cctv/')
        if user[0].password != signer.sign(password):
            request.session['login_password_right'] = False
            return redirect('/cctv/')
        if user[0].isSuperUser:
            request.session['login_is_super_user'] = True
        else:
            request.session['login_is_super_user'] = False
        if request.session.get('login'):
            del request.session['login']
        request.session['login'] = user[0]
        return redirect('/video/')

def register(request):
    return

def register_check(request):
    return

def video(request):
    imgs = Image.objects.all().order_by('add_time')
    context = {
        'img': imgs[0],
    }
    return render(request, 'cctv/video.html', context)

def video_refresh(request):
    imgs = Image.objects.all().order_by('add_time')
    imgs[0].delete()
    img_str = str(imgs[1].img)
    response = HttpResponse()
    response['Content-Type'] = "text/plain"
    response.write(img_str)
    return response
