"""firmware_upgrade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin,auth
from django.contrib.auth  import views
from ftp.views import *

urlpatterns = [
    url(r'^$',index),
    #url(r'^password_reset/$', views.password_reset, name='password_reset'),
    #url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
    #    'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    #url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^admin/login/$',login,name="login"),
    url(r'^admin/', admin.site.urls),
    url(r'^password_change/$', views.password_change, name='password_change'),
    url(r'^password_change/done/$', views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', views.password_reset_complete, name='password_reset_complete'),

    #url(r'^reset_pwd/$',reset_password),
    #url(r'^login/',login),
    #url(r'^register/$',RegisterView.as_view(),name='register')
    url(r'^register/$',register),
    url(r'^get_code/$',get_verify_code),
    #url(r'^tree(?P<path>(?:(?:/[^/]+)+|/?))', logined_handler),
]
