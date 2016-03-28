#coding: utf-8
from django.contrib import admin
import os
from glob import glob
import json
import shutil



# Register your models here.
from django.conf import settings
from .models import FtpUser,Product,FileType,FileVer
from .forms import FtpUserChangeForm,FtpUserCreationForm,FileVerionForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_permission_codename
from django.forms import FileInput,Select


def update_json(product_dir):

    plist = glob("%s/*/*/*" % product_dir)
    print "dir list",plist
    jdict = {}
    pdlen = len(product_dir)+1
    for item in plist:
        if not cmp('txt',item[-3:]):
            continue
        itlst = item[pdlen:].split('/')
        key = itlst[0]
        if not jdict.has_key(key):
            jdict[key] = []
        jdict[key].append(itlst[1])
    with open("%s/version.json" % product_dir,'wt') as fd:
        fd.write(json.dumps(jdict,sort_keys=True,indent=4,separators=(',',':')))


class PlatormInline(admin.TabularInline):
    model = FileType

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
#    inlines = [PlatormInline,]
    actions = ['delete_product']


    def delete_product(self,request,queryset):
        for obj in  queryset:
            try:
                shutil.rmtree('/'.join([settings.MEDIA_ROOT,request.user.email,obj.name]))
            except OSError:
                pass
            self.message_user(request,u'%s 删除成功' % obj.name)
            obj.delete()

    def get_actions(self,request):
        actions = super(ProductAdmin,self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_list_display_links(self,request,list_display):
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            return None

    def get_queryset(self,request):
        qs  = super(ProductAdmin,self).get_queryset(request)
        return qs.filter(ftp_user=request.user)

    def save_model(self,request,obj,form,change):
        obj.ftp_user = request.user
        obj.save()
        pdir = "/".join([settings.MEDIA_ROOT,request.user.email,obj.name])
        print "create dir ",pdir
        if not os.path.exists(pdir):
            os.makedirs(pdir)
    
    delete_product.short_description = u'选择删除产品'



class FtpUserAdmin(UserAdmin):
    actions = None
    fieldsets = (
            (_(u'更改密码'),{'fields':('password',)}),
            #(_(u'公司名称'),{'fields':('name',)}),
            #(_(u'注册时间'),{'fields':('date_joined',)}),
            (_(u'权限'),{'fields':('user_permissions','groups','is_active','is_staff')}),
            #(_(u'登录管理'),{'fields':('is_staff',)}),
            #(_(u'激活'),{'fields':('is_active',)}),
            )

    normal_fieldsets = (
            (_(u'更改密码'),{'fields':('password',)}),
              )  

    add_fieldsets = (
            (None,{
                'classes':('wide',),
                'fields':('email','password','password2')}
                ),
            )
    form = FtpUserChangeForm
    add_form = FtpUserCreationForm
    list_display = ('name','email','is_active','is_staff','reg_ip','date_joined','last_login')
    search_fields = ('email','name')
    ordering = ('email',)

    #def has_delete_permission(self,request,obj=None):
    #    return False

    def get_fieldsets(self,request,obj=None):
        if request.user.is_superuser:
            return self.fieldsets
        else:
            return self.normal_fieldsets

    def get_queryset(self,request):
        qs  = super(FtpUserAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(name=request.user)


class VerionInline(admin.TabularInline):
    model = FileVer

class FileTypeAdmin(admin.ModelAdmin):
    #actions = None
    list_display = ('get_product','name',)
    #inlines = [VerionInline]
    actions = ['delete_platform']
    
    def delete_platform(self,request,queryset):
        pdir_list = set()
        for obj in queryset:
            product = obj.product_name
            product_dir  = '/'.join([settings.MEDIA_ROOT,request.user.email,product.name])
            pdir_list.add(product_dir)
            platform_dir  = '/'.join([settings.MEDIA_ROOT,request.user.email,product.name,obj.name])
            try:
                shutil.rmtree(platform_dir)
            except OSError:
                pass
            self.message_user(request,u'%s 删除成功' % obj.name)
            obj.delete()
        l = list(pdir_list)
        for p in l:
            update_json(p)

    def has_change_permission(self,request,obj=None):
        if obj:
            return False
        return super(FileTypeAdmin,self).has_change_permission(request,obj)

    def get_list_display_links(self,request,list_display):
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            return None

    def get_actions(self,request):
        actions = super(FileTypeAdmin,self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_queryset(self,request):
        qs  = super(FileTypeAdmin,self).get_queryset(request)
        #print "request user objects",request.user.objects.all()
        product_obj = Product.objects.filter(ftp_user = request.user)
        #print "get querysets ",product_obj
        return qs.filter(product_name__in=list(set(product_obj)))

    
    def get_form(self,request,obj=None,**kwargs):
        form = super(FileTypeAdmin,self).get_form(request,obj,**kwargs)
        form.base_fields['product_name'].queryset = Product.objects.filter(ftp_user = request.user)
        return form

    def save_model(self,request,obj,form,change):
        obj.ftp_user = request.user
        obj.save()

    def get_product(self,obj):
        return unicode(obj.product_name.name)
    get_product.short_description = u'产品名称'
    delete_platform.short_description = u'删除'

    


    


class VerionAdmin(admin.ModelAdmin):
    #actions = None

    list_display = ('get_product','get_platform','ver_name','commit')
    #ordering = ('',)


    actions = ['delete_version']

    def get_actions(self,request):
        actions = super(VerionAdmin,self).get_actions(request)
        del actions['delete_selected']
        return actions

        

    def get_list_display_links(self,request,list_display):
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            return None


    #def __init__(self,*args,**kwargs):
    #    super(VerionAdmin,self).__init__(*args,**kwargs)
    #    #self.list_display_links=(None,)

    def delete_version(self,request,queryset):
        pdir_list = set()
        for obj in queryset:
            platform = obj.target_name
            product = platform.product_name
            ver_name = obj.ver_name
            tname = obj.target_name
            product_dir  = '/'.join([settings.MEDIA_ROOT,request.user.email,product.name])
            pdir_list.add(product_dir)
            ver_dir  = '/'.join([settings.MEDIA_ROOT,request.user.email,product.name,platform.name,ver_name])
            try:
                shutil.rmtree(ver_dir)
            except OSError:
                pass
            obj.delete()
            self.message_user(request,u'%s 删除成功' % ver_name)
        l = list(pdir_list)
        for p in l:
            update_json(p)
        



    def get_form(self,request,obj=None,**kwargs):
        form = super(VerionAdmin,self).get_form(request,obj,**kwargs)
        pq = Product.objects.filter(ftp_user=request.user)
        tn = FileType.objects.filter(product_name__in = pq)
        #form.base_fields['name'].queryset = pq
        form.base_fields['target_name'].queryset = form.base_fields['target_name'].queryset.filter(product_name__in = pq)
        if obj:
            #form.base_fields['ver_name'].widget.attrs['readonly'] = True
            print "base_fields type",type(form.base_fields)
            
            for w in form.base_fields.values():
                #if isinstance(w,FileInput):
                #    w.widget.attrs['disabled'] = True
                #w.widget.attrs['disabled'] = True
                w.widget.attrs['readonly'] = True
        return form

    def has_change_permission(self,request,obj=None):
        if obj:
            return None
        return super(VerionAdmin,self).has_change_permission(request,obj)
    
    def get_queryset(self,request):
        qs = super(VerionAdmin,self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if qs:
            pq = Product.objects.filter(ftp_user=request.user)
            tn = FileType.objects.filter(product_name__in = pq)
            return qs.filter(target_name__in=tn)

        return qs
    
    def save_model(self,request,obj,form,change):
        obj.save()
        platform = obj.target_name
        product = platform.product_name
        product_dir  = '/'.join([settings.MEDIA_ROOT,request.user.email,product.name])
        txtfile = "/".join([product_dir,platform.name,obj.ver_name,'Update Notes.txt'])
        if os.path.exists(txtfile):
            os.remove(txtfile)
        with open(txtfile,'wt') as fd:
            fd.write(obj.commit.encode('UTF-8'))
        update_json(product_dir)




    def get_platform(self,obj):
        return unicode(obj.target_name.name)

    def get_product(self,obj):
        return unicode(obj.target_name.product_name.name)
    get_product.short_description = u'产品名称'
    get_platform.short_description=u'平台类型'
    delete_version.short_description = u'删除'

            



    
        

    
    


#admin.site.register(Commpany)
admin.site.register(FtpUser,FtpUserAdmin)
#admin.site.register(FtpUser)
admin.site.register(Product,ProductAdmin)
admin.site.register(FileType,FileTypeAdmin)
admin.site.register(FileVer,VerionAdmin)
