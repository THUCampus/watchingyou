from django.conf.urls import url

from . import views

app_name = 'cctv'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/check/$', views.login_check, name='login_check'),
    url(r'^menu/$', views.menu, name='menu'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/check/$', views.register_check, name='register_check'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^settings/check/$', views.settings_check, name='settings_check'),
    url(r'^video/camera-(?P<camera>[^/]+)/detect-(?P<detect>[^/]+)/$', views.video, name='video'),
    url(r'^video/refresh/camera-(?P<camera>[^/]+)/detect-(?P<detect>[^/]+)/$', views.video_refresh, name="video_refresh"),
    url(r'^video/v2/camera-(?P<camera>[^/]+)/detect-(?P<detect>[^/]+)/$', views.video_v2, name="video_v2"),
    url(r'^video/stream/camera-(?P<camera>[^/]+)/detect-(?P<detect>[^/]+)/$', views.video_stream, name="video_stream"),
    url(r'^websocketLink/(?P<username>\w+)', views.websocketLink),
    url(r'^test/$', views.testview),
]