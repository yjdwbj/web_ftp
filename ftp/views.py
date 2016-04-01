#coding: utf-8
from .forms import RegisterForm,CustomAuthForm,ResetPassword
import os
from django.shortcuts import render
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import (
        REDIRECT_FIELD_NAME,login as auth_login
        )
from django.utils.http import is_safe_url
from django.template.response import TemplateResponse
from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import password_reset as django_password_reset
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate,login
from django.core.servers.basehttp import get_internal_wsgi_application
from notebook.tree.handlers import TreeHandler
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from .captcha import get_code
    



@csrf_exempt
def index(request):
    if request.method == 'POST':
        data = request.POST.get('register','')
        if data:
            #render_to_response('register.html',context_instance=RequestContext(request))
            return HttpResponseRedirect("/register/")
        return login_view(request)
    return HttpResponseRedirect("/admin/")



@csrf_exempt
def get_verify_code(request):
    txt,img = get_code()
    request.session[txt] = request.META['REMOTE_ADDR']
    return HttpResponse(img,'image/png')


@csrf_exempt
def password_reset(*args,**kwargs):
    kwargs['password_reset_form'] = ResetPassword
    django_password_reset(*args,**kwargs)

def reset_password(request):
    if request.method == 'POST':
        form = ResetPassword(request.POST,request=request)
        if form.is_valid():
            return HttpResponse('registration/password_reset_email.html')
        else:
            return render_to_response('registration/password_reset_email.html',{'form':form})

    return render_to_response('registration/password_reset_form.html',{'form':ResetPassword()})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        #print "request --------------",request.__dict__
            
        form = RegisterForm(request.POST,request=request)
        if form.is_valid():
            if form.get_captcha in request.session:
                form.save()
                return HttpResponseRedirect('/admin/login/')
            else:
                form.add_error('captcha',u'验证码不正确')
                form.fields['captcha'].widget.attrs['value'] = ''
                return render_to_response('register.html',{'form': form})
        else:
            form.fields['captcha'].widget.attrs['value'] = ''
            return render_to_response('register.html', {'form': form})
        
    return render_to_response('register.html', {'form': RegisterForm()})


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request,template_name='admin/login.html',
        redirect_field_name=REDIRECT_FIELD_NAME,
        authentication_form = CustomAuthForm,
        extra_context=None):
    redirect_to = request.POST.get(redirect_field_name,
            request.GET.get(redirect_field_name,''))

    if request.method == 'POST':
        form = authentication_form(request,data=request.POST)
        if form.is_valid():
            if form.get_captcha() in request.session:
                #if not is_safe_url(url=redirect_to, host=request.get_host()):
                #    redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
                # Okay, security check complete. Log the user in.
                auth_login(request, form.get_user())
                return HttpResponseRedirect(redirect_to)
            else:
                form.fields['captcha'].widget.attrs['value'] = ''
                form.add_error('captcha',u'验证码不正确')

    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)



