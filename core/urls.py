from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^narratives/id/(?P<id>\d)$', views.narrative, name="narrative_id"),
    url(r'^narratives/create$', views.create_narrative, name="create_narrative"),
    url(r'^narratives/check$', views.check_narratives, name="check_narratives"),
    url(r'^narratives/flush/all$', views.flush_narrative, name="flush_narrative_all"),
    url(r'^narratives/flush/(?P<slug>[\w-]+)$', views.flush_narrative, name="flush_narrative"),
    url(r'^narratives/(?P<slug>[\w-]+)$', views.narrative, name="narrative_slug"),
    url(r'^narratives/(?P<slug>[\w-]+)/all$', views.narrative, name="narrative_slug_all", kwargs={'show_all': True}),
    url(r'^narratives/(?P<slug>[\w-]+)/read_to$', views.set_read_to_narrative, name="narrative_read_to"),
    url(r'^narratives/(?P<slug>[\w-]+)/article_vote$', views.article_vote, name="article_vote"),
)

