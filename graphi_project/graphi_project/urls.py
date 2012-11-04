# -*- coding: utf-8 -*-
"""
Author: David Wong <davidwong.xc@gmail.com>
License: 3 clause BSD license

"""

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', 'graphi_main.views.home'),
    url(r'^graphing/?$', 'graphi_main.views.graphing'),
    url(r'^parsepython/?$', 'graphi_main.views.parsepython'),
    url(r'^parsepython-example/?$', 'graphi_main.views.parsepython_example'),
    url(r'^about/?$', 'graphi_main.views.about'),
    url(r'^contact/?$', 'graphi_main.views.contact'),
    url(r'^thanks/?$', 'graphi_main.views.thanks'),
    url(r'^hireme/?$', 'graphi_main.views.hire_me'),
    url(r'^faq/?$', 'graphi_main.views.faq'),
    url(r'^features/?$', 'graphi_main.views.features'),
    url(r'^termsofservice/?$', 'graphi_main.views.terms'),
      
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
