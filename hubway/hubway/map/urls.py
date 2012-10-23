from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='map-home'),
    url(r'districts/$', views.districts, name='map-districts'),
    url(r'^bounds/$', views.bounds, name='map-bounds'),
    url(r'^routes/$', views.routes, name='map-route'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
