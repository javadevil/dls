from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^latest','orbit.views.latest',name='latest'),
)