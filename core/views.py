# Create your views here.
import json
import urllib2
import xml.utils.iso8601 as iso8601
import lxml.html
import itertools
from datetime import datetime, date, timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Narrative, GuardianSearch, ReadTo, Article

def home(request):
  narratives = Narrative.objects.all()

  for narrative in narratives:
    last_viewed_date = date.today()
    if not request.user.is_anonymous():
      try:
        read_to = ReadTo.objects.get(user=request.user,
                                     narrative=narrative)
        last_viewed_date = read_to.date
      except ReadTo.DoesNotExist:
        pass

    count = Article.objects.filter(narrative=narrative,
                                   date__gt=last_viewed_date).count()

    narrative.new_count = count

    if narrative.last_updated < datetime.now() - timedelta(7):
      narrative.dormant = True
    else:
      narrative.dormant = False

  narratives = sorted(narratives, key=lambda narrative: narrative.last_updated, reverse=True)

  return render_to_response('home.html', {'narratives': narratives})

def narrative(request, id=None, slug=None, show_all=False):
  narrative = None
  if id is not None:
    narrative = Narrative.objects.get(pk=id)
  if slug is not None:
    narrative = Narrative.objects.get(slug=slug)

  if request.user.is_anonymous():
    read_to = None
  else:
    try:
      read_to = ReadTo.objects.get(user=request.user,
                                   narrative=narrative)
    except ReadTo.DoesNotExist:
      read_to = None
  
  articles = list(narrative.article_set.order_by('-date'))

  for i, result in enumerate(articles):
    result.ordinal = i

  unread_i = 0
  if read_to is not None:
    for i in range(len(articles)):
      if articles[i].date <= read_to.date:
        articles[i].read_to = True
        if i != 0:
          articles[i-1].last_unread = True
        unread_i = i
        break

    if unread_i == 0:
      show_all = True

    if not show_all:
      articles = articles[:unread_i]

  day_grouped = itertools.groupby(articles, lambda article: article.date.date()) 
  grouped_articles = [(date, list(articles)) for date, articles in day_grouped]

  read_to.date = datetime.now()
  read_to.save()

  return render_to_response('narrative.html', {'narrative': narrative,
                                               'grouped_articles': grouped_articles,
                                               'show_all': show_all,})

def create_narrative(request):
  return render_to_response('narrative_create.html', {})

def flush_narrative(request, slug=None):
  if slug is None:
    narratives = Narrative.objects.all()
  else:
    narratives = [Narrative.objects.get(slug=slug)]

  for narrative in narratives:
    for search in narrative.guardiansearch_set.all():
      search.cache = ""
      search.save()

    narrative.populate_articles()

  if slug is not None:
    return HttpResponseRedirect(reverse('narrative_slug', kwargs={'slug': slug}))
  else:
    return HttpResponseRedirect(reverse('home'))

def check_narratives(request):
  """
    Find all narratives which are due to be checked, then set their next check time:
  """

  now = datetime.now()
  day_ago = now - timedelta(1)
  narratives = Narrative.objects.all()
  for narrative in narratives:
    if narrative.next_check <= now:
      for search in narrative.guardiansearch_set.all():
        search.cache = ""
        search.save()

      narrative.populate_articles()
      new_article_count = Article.objects.filter(narrative=narrative,date__gt=day_ago).count()
     
      # No new articles in the last 24 hours, check in 6 hours 
      if new_article_count == 0:
        new_gap = timedelta(0,0,0,0,0,6)
      # New articles in last 24 hours, check in 1 hour
      else:
        new_gap = timedelta(0,0,0,0,0,1)
      narrative.last_check = now
      narrative.next_check = narrative.last_check + new_gap
      narrative.save()

  return HttpResponseRedirect('/')

def set_read_to_narrative(request, slug):
  date = request.POST['date']
  date = datetime.fromtimestamp(iso8601.parse(date))

  if request.user.is_anonymous():
    return HttpResponse('')

  narrative = Narrative.objects.get(slug=slug)
  
  try:
    read_to = ReadTo.objects.get(user=request.user, narrative=narrative)
  except ReadTo.DoesNotExist:
    read_to = None

  if read_to is not None:
    read_to.date = date
    read_to.save()
  else:
    read_to = ReadTo.objects.create(user=request.user,
                                    narrative=narrative,
                                    date=date)

  
  return HttpResponse('')
