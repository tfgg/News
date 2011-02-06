from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^narratives/id/(?P<id>\d)$', views.narrative, name="narrative_id"),
    url(r'^narratives/(?P<slug>[\w-]+)$', views.narrative, name="narrative_slug"),
)

