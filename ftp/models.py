#coding: utf-8
from __future__ import unicode_literals
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.html import format_html
from datetime import datetime

# Create your models here.

class Meta:
    app_label=u"固件管理"
    list_instances = False


class FtpUserManager(BaseUserManager):
    def _create_user(self,email,password,is_staff,is_superuser,**extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError(u'必须输入邮箱地址')
        email = self.normalize_email(email)

        user = self.model(email = email,is_superuser=is_superuser,is_staff=is_staff,
                                    last_login=now,is_active = True,date_joined=now,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email,password=None,**extra_fields):
        return self._create_user(email,password,False,False,**extra_fields)

    def create_superuser(self,email,password=None,**extra_fields):
        return self._create_user(email,password,True,True,**extra_fields)



class FtpUser(AbstractBaseUser,PermissionsMixin):
    class Meta:
        verbose_name = u"帐户"
        verbose_name_plural=verbose_name
        unique_together = ("name","email")
    #User = models.CharField(max_length=50,primary_key=True,blank=False,verbose_name=u"用户名")
    name = models.CharField(max_length=256,blank=False,verbose_name=u"公司名字")
    email = models.EmailField(primary_key=True,unique=True,blank=False,verbose_name=u"邮箱")
    #password = models.CharField(max_length=50,blank=False,verbose_name=u"密码")
    phone_num= models.CharField(default='138000138000',max_length=15,verbose_name=u"联系电话")
    reg_ip = models.GenericIPAddressField(editable=False,default='127.0.0.1',max_length=15,verbose_name=u"申请IP")
    is_active = models.BooleanField(default=False,verbose_name=u"激活")
    is_staff = models.BooleanField(default=False,verbose_name=u"登录管理")
    #is_superuser = models.BooleanField(default=False,verbose_name=u"超级用户")
    
    date_joined = models.DateTimeField(default=timezone.now,verbose_name=u'注册时间')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone_num','reg_ip']

    objects = FtpUserManager()

    def get_absolute_url(self):
        return "/user/%s/" % urlquote(self.email)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name = u'产品管理'
        verbose_name_plural=u'产品管理'
        unique_together = ("ftp_user","name")
        ordering= ['name',]

    name = models.CharField(max_length=256,blank=False,verbose_name=u'产品名称')
    ftp_user= models.ForeignKey(FtpUser,editable=False,on_delete=models.CASCADE,null = False,verbose_name=u"用户名")
    def __unicode__(self):
        return self.name

    def filter_link(self):
        url = "?product=%d" % self.id
        return format_html('<a href=%s>%s</a>' % (url,self.name))
    
    filter_link.allow_tags = True

class FileType(models.Model):
    class Meta:
        verbose_name = u"平台类型"
        verbose_name_plural=u"平台类型"
        unique_together = ("name","product_name")
    product_name = models.ForeignKey(Product,blank=False,verbose_name=u'产品名称')
    #ftp_user= models.ForeignKey(FtpUser,editable=False,on_delete=models.CASCADE,null = False,verbose_name=u"用户名")
    name = models.CharField(max_length=256,null=False,blank= False,verbose_name=u'平台名称')
    def __unicode__(self):
        return  self.product_name.name + " | " + self.name

def get_upload_dir(req,filename):
    tname  = req.target_name
    print "platform ",tname.__dict__
    pname = tname.product_name
    print "product ",pname.__dict__
    fdir = '/'.join([settings.MEDIA_ROOT,pname.ftp_user.email,pname.name,tname.name,req.ver_name])
    #fdir = '/'.join([settings.MEDIA_ROOT,product.ftp_user.email,req.name.name,req.target_name.target_name,req.ver_name])
    fdir = unicode(fdir)
    
    if os.path.exists(fdir):
        try:
            os.makedirs(fdir)
        except OSError:
            pass
    filepath = '/'.join([fdir,req.file_name.name])
    if os.path.isfile(filepath):
        os.remove(filepath)
    return filepath
    


class CustomFileField(models.FileField):
    def __init__(self,*args,**kwargs):
        self.blacklist =kwargs.pop("blacklist")
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(CustomFileField,self).__init__(*args,**kwargs)

    def clean(self,*args,**kwargs):
        data = super(CutsomFileField,self).clean(*args,**kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.blacklist:
                raise forms.ValidationError(_(u'文件类型不支持'))
            else:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_(u'文件超过最大上传限制%s' %
                                        filesizeformat(self.max_upload_size)))
        except AttributeError:
            pass
        return data



class FileVer(models.Model):
    class Meta:
        verbose_name = u'版本列表'
        verbose_name_plural=u'版本列表'
        unique_together = ("ver_name","target_name",)


    
    #ftp_user = models.ForeignKey(FtpUser,editable=False,on_delete=models.CASCADE,null = False,verbose_name=u"用户名")
    #name = models.ForeignKey(Product,on_delete = models.CASCADE,verbose_name=u'产品名')
    #target_name = models.ForeignKey(FileType,on_delete=models.CASCADE,verbose_name=u'文件类型')
    target_name = models.ForeignKey(FileType,on_delete=models.CASCADE,verbose_name=u'平台类型')
    ver_name = models.CharField(max_length=256,blank=False,verbose_name=u'版本')
    #file_name= models.FileField(upload_to = get_upload_dir,max_length=1024,blank=False,verbose_name=u'文件名',help_text=u'文件大小不能超过10M,不能上传txt文件')
    file_name= CustomFileField(blacklist='txt',max_upload_size=10*1024*1024,
                                upload_to = get_upload_dir,max_length=1024,
                                blank=False,verbose_name=u'文件名',
                                help_text=u'文件大小不能超过10M,不能上传txt文件')
    date = models.DateTimeField(default=timezone.now,editable=False,blank=False,verbose_name=u'创建时间')
    commit = models.TextField(max_length=1024,verbose_name=u'备注')

    def __unicode__(self):
        return self.ver_name






