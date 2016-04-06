#coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.forms import AuthenticationForm,PasswordResetForm
from django.conf import settings
from .models import FtpUser,FileVer,Product
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.admin.templatetags.admin_static import static

class FtpUserCreationForm(UserCreationForm):
    def __init__(self,*args,**kargs):
        super(FtpUserCreationForm,self).__init__(*args,**kargs)

    class Meta:
        model = FtpUser
        fields = ('email',)



class FtpUserChangeForm(UserChangeForm):
    def __init__(self,*args,**kargs):
        super(FtpUserChangeForm,self).__init__(*args,**kargs)

    class Meta:
        model = FtpUser
        fields = ('email',)


class FileVerionForm(forms.ModelForm):
    class Meta:
        model = FileVer
        exclude = ()
        
    def __init__(self,*args,**kwargs):
        super(FileVerionForm,self).__init__(*args,**kwargs)
        if self.instance:
            self.fields['product_name'].get_queryset = Product.objects.filter(ftp_user=None)


class ResetPassword(PasswordResetForm):
    email = forms.EmailField(
            label=u'邮箱',
            help_text=u'邮箱可用于登录，最重要的是需要邮箱来找回密码',
            max_length = 50,
            initial='',
            #widget=forms.TextInput(attrs={'class':'form-control'}),
            )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ResetPassword, self).__init__(*args, **kwargs)

        
    def clean(self):
        cleaned_data = super(ResetPassword, self).clean()
        user = FtpUser.objects.filter(email = cleaned_data.get('email'))
        if len(user) == 0:
            raise forms.ValidationError(u'没有查询到此邮箱注册记录，请重新输入')




class RegisterForm(forms.Form):
#    UserName = forms.CharField(label=u"用户名",help_text=u'用户名用于登录，不能超过50个字符，不能包含空格与@字符',
#    max_length=50,
#    initial='',
#    widget=forms.TextInput(attrs={'class':'form-control'}),
#    )
    password = forms.CharField(
            label=u'密码',
            help_text=u'密码长度 6 ~ 12',
            min_length=6,max_length=12,
            widget= forms.PasswordInput(attrs={'class':'form-control'}),
            )
    confirm_password = forms.CharField(
            label=u'确认密码',
            min_length=6,max_length=12,
            widget= forms.PasswordInput(attrs={'class':'form-control'}),
            help_text=u'密码长度 6 ~ 12,两次输入必须一样',
            )
    commpanyname = forms.CharField(
            label=u'公司名称',
            min_length=4,max_length=50,
            widget = forms.TextInput(attrs={'class':'form-control'}),
            help_text=u'请填写贵公司名，方便我们工作人员审核',
            )

    email = forms.EmailField(
            label=u'邮箱',
            help_text=u'邮箱可用于登录，最重要的是需要它来找回密码',
            max_length = 50,
            initial='',
            widget=forms.TextInput(attrs={'class':'form-control'}),
            )
    phone = forms.CharField(
            label=u'公司电话',
            min_length=11,max_length=15,
            widget = forms.TextInput(attrs={'class':'form-control'}),
            help_text=u'请填写有效的固话或手机，方便我们联系到您',
            )

    captcha = forms.CharField(
            label=u'验证码',
            min_length=6,max_length=6,
            widget = forms.TextInput(attrs={'class':'form-verify'}),
            )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].initial=''

    def clean_username(self):
        username = self.cleaned_data['commpanyname']
        if ' ' in username:
            raise forms.ValidationError(u'名称中包含空格')
        if '@' in username:
            raise forms.ValidationError(u'名称中包含@')

        res = FtpUser.objects.filter(email=username)
        if len(res):
            raise forms.ValidationError(u'用户已经存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        res = FtpUser.objects.filter(email=email)
        if len(res) != 0:
            raise forms.ValidationError(u'此邮箱已经注册，请重新输入')
        return email

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(u'两次密码输入不一致，请重新输入')
        captcha = cleaned_data.get('captcha')
        if not captcha or len(captcha) != 6:
            raise forms.ValidationError(u'验证码不正确')

            
    def get_captcha(self):
        code = self.data['captcha']
        if not code or len(code) != 6:
            raise forms.ValidationError(u'请输入正确的验证码')
        return code

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        company = self.cleaned_data['commpanyname']
        phone = self.cleaned_data['phone']
        d = {'name':company,'reg_ip':self.request.META.get('REMOTE_ADDR'),'phone_num':phone}
        user = FtpUser.objects.create_user(email,password,**d)
        user.save()
        g = Group.objects.get(id=1)
        g.user_set.add(user)


    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'core.js',
            'vendor/jquery/jquery%s.js' % extra,
            'jquery.init.js',
            'admin/RelatedObjectLookups.js',
            'actions%s.js' % extra,
            'urlify.js',
            'prepopulate%s.js' % extra,
            'vendor/xregexp/xregexp.min.js',
        ]
        return forms.Media(js=[static('admin/js/%s' % url) for url in js])


class CustomAuthForm(AuthenticationForm):
    
    captcha = forms.CharField(
            label=u'验证码',
            min_length=6,max_length=6,
            widget = forms.TextInput(attrs={'class':'form-verify'}),
            )

    def __init__(self,request=None,*args,**kwargs):
        super(CustomAuthForm,self).__init__(*args,**kwargs)

    def clean(self):
        captcha = self.cleaned_data.get('captcha')
        if not captcha or len(captcha) != 6:
            raise forms.ValidationError(
                    u'请输入正确的验证码'
                    )
        return super(CustomAuthForm,self).clean()
            #self.confirm_login_allowed(self.user_cache)

        #return self.cleaned_data

    def get_captcha(self):
        code = self.data['captcha']
        if not code or len(code) != 6:
            self.add_error('captcha',u'请输入正确的验证码')
        return code

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'core.js',
            'vendor/jquery/jquery%s.js' % extra,
            'jquery.init.js',
            'admin/RelatedObjectLookups.js',
            'actions%s.js' % extra,
            'urlify.js',
            'prepopulate%s.js' % extra,
            'vendor/xregexp/xregexp.min.js',
        ]
        return forms.Media(js=[static('admin/js/%s' % url) for url in js])
