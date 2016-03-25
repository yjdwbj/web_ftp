#coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django import forms
from .models import FtpUser,FileVer,Product
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

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





class RegisterForm(forms.Form):
#    UserName = forms.CharField(label=u"用户名",help_text=u'用户名用于登录，不能超过50个字符，不能包含空格与@字符',
#    max_length=50,
#    initial='',
#    widget=forms.TextInput(attrs={'class':'form-control'}),
#    )
    Password = forms.CharField(
            label=u'密码',
            help_text=u'密码长度 6 ~ 12',
            min_length=6,max_length=12,
            widget= forms.PasswordInput(attrs={'class':'form-control'}),
            )
    Confirm_password = forms.CharField(
            label=u'确认密码',
            min_length=6,max_length=12,
            widget= forms.PasswordInput(attrs={'class':'form-control'}),
            )
    CommpanyName = forms.CharField(
            label=u'公司名称',
            min_length=4,max_length=50,
            widget = forms.TextInput(attrs={'class':'form-contron'}),
            )

    Email = forms.EmailField(
            label=u'邮箱',
            help_text=u'邮箱可用于登录，最重要的是需要邮箱来找回密码',
            max_length = 50,
            initial='',
            widget=forms.TextInput(attrs={'class':'form-control'}),
            )
    Phone = forms.CharField(
            label=u'公司电话',
            min_length=11,max_length=15,
            widget = forms.TextInput(attrs={'class':'form-control'}),
            )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['CommpanyName']
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
        password = cleaned_data.get('Password')
        confirm_password = cleaned_data.get('Ponfirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(u'两次密码输入不一致，请重新输入')

    def save(self):
        email = self.cleaned_data['Email']
        password = self.cleaned_data['Password']
        company = self.cleaned_data['CommpanyName']
        phone = self.cleaned_data['Phone']
        d = {'name':company,'reg_ip':self.request.META.get('REMOTE_ADDR'),'phone_num':phone}
        user = FtpUser.objects.create_user(email,password,**d)
        user.save()
        g = Group.objects.get(id=1)
        g.user_set.add(user)
