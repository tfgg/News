from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^narratives/id/(?P<id>\d)$', views.narrative, name="narrative_id"),
    url(r'^narratives/create$', views.create_narrative, name="create_narrative"),
    url(r'^narratives/flush/(?P<slug>[\w-]+)$', views.flush_narrative, name="flush_narrative"),
    url(r'^narratives/(?P<slug>[\w-]+)$', views.narrative, name="narrative_slug"),
)

