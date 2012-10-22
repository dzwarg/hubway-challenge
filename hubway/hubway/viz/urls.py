from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='viz-home'),
    url(r'counts/$', views.counts, name='viz-counts'),
    url(r'trips/(?P<number>.+)/$', views.trips, name='viz-trips'),
    url(r'volume/(?P<number>.+)/$', views.volume, name='viz-volume'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
