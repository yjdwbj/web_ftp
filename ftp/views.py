#coding: utf-8
from .forms import RegisterForm
import os
from django.shortcuts import render
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.views.decorators.csrf import csrf_exempt

from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate,login
from django.core.servers.basehttp import get_internal_wsgi_application
from notebook.tree.handlers import TreeHandler
from .captcha import get_code
    



def login_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')

    user = auth.authenticate(username=username,password=password)
    if user is not None and user.is_active:
        auth.login(request,user)
        return HttpResponseRedirect("/account/loggedin/")
    else:
        return HttpResponseRedirect("/account/invalid/")

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
def logined_handler(request):
    th = TreeHandler(get_internal_wsgi_application(),request)
    return th.render_template('tree.html')

@csrf_exempt
def get_verify_code(request):
    txt,img = get_code()
    print "code is",txt
    return HttpResponse(img,'image/png')




class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('blog_index')

    def form_valid(self,form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        login(self.request,user)
        return super(RegisterView,self).form_valid(form)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        print "request --------------",request.__dict__
        if request.POST.get('login_btn',''):
            return HttpResponseRedirect('/admin/login/')
            
        form = RegisterForm(request.POST,request=request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin/login/')
        else:
            return render_to_response('register.html', {'form': form})
    return render_to_response('register.html', {'form': RegisterForm()})
