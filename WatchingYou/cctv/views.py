# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.http import HttpResponse

from .models import User, Image, Camera

def index(request):
    if request.session.get('login'):
        return redirect('/cctv/menu/')

    if request.method == 'GET':
        context = {
            'user_exists': True,
            'password_right': True,
        }
        return render(request, 'cctv/index.html', context)
    elif request.method == 'POST':
        print("post")
        context = {
            'user_exists': True,
            'password_right': True,
        }
        return render(request, 'cctv/index.html', context)

def login_check(request):
    if request.session.get('login'):
        return redirect('/cctv/menu/')

    if request.method == 'POST':
        login_user_exists = True
        login_password_right = True
        user = User.objects.filter(name=request.POST['login_user_name'])
        password = request.POST['login_user_password']

        if not user:
            login_user_exists = False
        elif not user[0].is_password_right(password):
            login_password_right = False

        if login_user_exists and login_password_right:
            if request.session.get('login'):
                del request.session['login']
            request.session['login'] = user[0].name
            request.session['isSuperUser'] = user[0].isSuperUser
            return redirect('/cctv/menu/')
        else:
            print('fail')
            context = {
                'user_exists': login_user_exists,
                'password_right': login_password_right,
            }
            return render(request, 'cctv/index.html', context)
    elif request.method == 'GET':
        return redirect('/cctv/')

def menu(request):
    if not request.session.get('login'):
        return redirect('/cctv/')

    if request.method == 'POST':
        print('post_to_menu')
        return
    elif request.method == 'GET':
        cameras = Camera.objects.all()
        detect_types = Image.objects.values('detection_type').distinct().order_by('-detection_type')
        context = {
            'user': request.session.get('login'),
            'isSuperUser': request.session.get('isSuperUser'),
            'cameras': cameras,
            'detect_types': detect_types,
        }
        return render(request, 'cctv/menu.html', context)

def register(request):
    if not request.session.get('login'):
        return redirect('/cctv/')
    if not request.session.get('isSuperUser'):
        return redirect('/cctv/menu/')

    if request.method == 'POST':
        print('post_to_settings')
        return
    elif request.method == 'GET':
        context = {
            'user_existed': False,
            'user_illegal': False,
            'password_illegal': False,
            'password_different': False,
        }
        return render(request, 'cctv/register.html', context)

def register_check(request):
    if not request.session.get('login'):
        return redirect('/cctv/')
    if not request.session.get('isSuperUser'):
        return redirect('/cctv/menu/')

    if request.method == 'POST':
        user_existed = False
        user_illegal = False
        password_illegal = False
        password_different = False
        user_name = request.POST['user_name']
        user_password = request.POST['user_password']
        user_password_confirm = request.POST['user_password_confirm']

        if not user_name:
            user_illegal = True
        elif len(user_name) > 20:
            user_illegal = True
        elif User.objects.filter(name=user_name):
            user_existed = True
        if not user_password:
            password_illegal = True
        elif len(user_password) > 20:
            password_illegal = True
        elif user_password != user_password_confirm:
            password_different = True

        if user_existed or user_illegal or password_illegal or password_different:
            context = {
                'user_existed': user_existed,
                'user_illegal': user_illegal,
                'password_illegal': password_illegal,
                'password_different': password_different,
            }
            return render(request, 'cctv/register.html', context)
        else:
            new_user = User(name=user_name, password=user_password)
            new_user.save()
            context = {
                'title': u'注册成功',
                'message': u'新用户注册成功',
                'destination': '/cctv/menu/',
            }
            return render(request, 'cctv/message.html', context)
    elif request.method == 'GET':
        return redirect('/cctv/register/')

def settings(request):
    if not request.session.get('login'):
        return redirect('/cctv/')

    if request.method == 'POST':
        print('post_to_settings')
        return
    elif request.method == 'GET':
        context = {
            'user': request.session.get('login'),
            'old_password_right': True,
            'new_password_illegal': False,
        }
        return render(request, 'cctv/settings.html', context)

def settings_check(request):
    if not request.session.get('login'):
        return redirect('/cctv/')

    if request.method == 'POST':
        user = User.objects.filter(name=request.session.get('login'))
        password = request.POST['old_user_password']
        new_password = request.POST['new_user_password']
        if not user:
            del request.session['login']
            context = {
                'title': u'错误',
                'message': u'用户不存在，请重新登陆',
                'destination': '/cctv/',
            }
            return render(request, 'cctv/message.html', context)
        elif not user[0].is_password_right(password):
            context = {
                'user': request.session.get('login'),
                'old_password_right': False,
                'new_password_illegal': False,
            }
            return render(request, 'cctv/settings.html', context)
        if not new_password:
            context = {
                'user': request.session.get('login'),
                'old_password_right': True,
                'new_password_illegal': True,
            }
            return render(request, 'cctv/settings.html', context)
        elif len(new_password) > 20:
            context = {
                'user': request.session.get('login'),
                'old_password_right': True,
                'new_password_illegal': True,
            }
            return render(request, 'cctv/settings.html', context)
        else:
            user[0].password = new_password
            user[0].password_en = False
            user[0].save()
            del request.session['login']
            context = {
                'title': u'修改成功',
                'message': u'密码修改成功，请重新登陆',
                'destination': '/cctv/',
            }
            return render(request, 'cctv/message.html', context)
    elif request.method == 'GET':
        return redirect('/cctv/settings/')


def video(request, camera, detect):
    if not request.session.get('login'):
        return redirect('/cctv/')
    camera_path = '/cctv/video/refresh/' + camera + '/' + detect +'/'
    cameras = Camera.objects.filter(camera_id=camera)
    if not cameras:
        return redirect('/cctv/menu/')
    camera = cameras[0]

    if request.method == 'POST':
        print('post_to_video')
        return
    elif request.method == 'GET':
        imgs = camera.image_set.filter(detection_type=detect).order_by('-add_time')
        if not imgs:
            print('no img')
            return render(request, 'cctv/video.html', {})
        context = {
            'img': str(imgs[0].img),
            'camera_path': camera_path,
        }
        print('img')
        return render(request, 'cctv/video.html', context)

def video_refresh(request, camera, detect):
    if not request.session.get('login'):
        return redirect('/cctv/')

    cameras = Camera.objects.filter(camera_id=camera)
    if not cameras:
        return redirect('/cctv/menu/')
    camera = cameras[0]

    if request.method == 'POST':
        print('post_to_video_fresh')
        return
    elif request.method == 'GET':
        response = HttpResponse()
        response['Content-Type'] = "text/plain"
        imgs = camera.image_set.filter(detection_type=detect).order_by('-add_time')
        if not imgs:
            print('no fresh img')
            return response
        img_str = str(imgs[0].img)
        print(img_str)
        response.write(img_str)
        return response

def logout(request):
    if not request.session.get('login'):
        return redirect('/cctv/')

    if request.method == 'POST':
        del request.session['login']
        request.session['isSuperUser'] = False
        return  redirect('/cctv/')
    elif request.method == 'GET':
        del request.session['login']
        request.session['isSuperUser'] = False
        return redirect('/cctv/')
