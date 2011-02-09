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
    if not request.user.is_anonymous():
      try:
        read_to = ReadTo.objects.get(user=request.user,
                                     narrative=narrative)
        count = Article.objects.filter(narrative=narrative,
                                       date__gt=read_to.date).count()
        narrative.new_count = count
      except ReadTo.DoesNotExist:
        pass

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

  return render_to_response('narrative.html', {'narrative': narrative,
                                               'grouped_articles': grouped_articles,
                                               'read_to': read_to,
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

    - If there's a new article, check again in 1 hour
    - If there's no new article, double the gap up to a max of 24 hours  
  """

  now = datetime.now()
  narratives = Narrative.objects.all()
  for narrative in narratives:
    print narrative.title, narrative.next_check
    if narrative.next_check <= now:
      article_count = len(narrative.results)
      narrative.results
      for search in narrative.guardiansearch_set.all():
        search.cache = ""
        search.save()
      narrative.results
      new_article_count = len(narrative.results) - article_count

      print narrative.title, new_article_count
      
      new_gap = timedelta(0,0,0,0,0,1)
      if new_article_count == 0:
        new_gap = (narrative.next_check - narrative.last_check)*2
        if new_gap > timedelta(1):
          new_gap = timedelta(1)
      narrative.last_check = now
      narrative.next_check = narrative.last_check + new_gap
      narrative.save()

      print narrative.last_check, narrative.next_check
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
