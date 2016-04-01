from django.contrib.admin.sites import AdminSite

class FtpSite(AdminSite):

    #def __init__(self,name='admin'):
    #    super(FtpSite,self).__init__(name=name)


    def get_app_list(self,request):

        applist = super(FtpSite,self).get_app_list(request)
        print "app list is",applist
        
    def get_urls(self):
        from django.conf.urls import url
        urls = super(FtpSite,self).get_urls()
        urls += [ 
                url(r'filter_view/$',self.admin_view)
                ]
        return urls
