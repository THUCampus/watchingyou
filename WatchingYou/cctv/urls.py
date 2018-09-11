from django.conf.urls import url

from . import views

app_name = 'cctv'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/check/$', views.login_check, name='login_check'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/check/$', views.register_check, name='register_check'),
    url(r'^video/$', views.video, name='video'),
    url(r'^video/refresh/$', views.video_refresh, name="video_refresh"),
]