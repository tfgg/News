import json
from datetime import datetime, date, timedelta
import xml.utils.iso8601 as iso8601
import lxml.html
import itertools

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

import gu

def strip_html(s):
  s = s.replace('</p>','\n')
  s = s.replace('<p>', '')
  s = s.replace('<br/>', '\n')
  try:
    t = lxml.html.fromstring(s)
    return t.text_content()
  except lxml.etree.ParserError:
    return s

def do_search(narrative):
  all_results = []
  for search in narrative.guardiansearch_set.all():
    results = search.do()
    for article in results:
      a = {}
      a['date'] = datetime.fromtimestamp(iso8601.parse(article['webPublicationDate']))
      a['istoday'] = (date.today() == a['date'].date())
      a['thisweek'] = (a['date'].date() > date.today() - timedelta(7))
      a['search'] = [search]
      
      if 'fields' in article and 'body' in article['fields']:
        if article['fields']['body'] == '<!-- Redistribution rights for this field are unavailable -->' or len(article['fields']['body']) == 0:
          a['firstpara'] = ""
        else:
          a['firstpara'] = strip_html(article['fields']['body']).split('\n')[0]
      else:
          a['firstpara'] = ""
      a['data'] = article
      all_results.append(a)
  all_results = sorted(all_results, key=lambda article: article['date'], reverse=True)

  # Remove duplicates
  results = []
  grouped = itertools.groupby(all_results, lambda article: article['data']['id'])
  for group, articles in grouped:
    articles = list(articles)
    for a in articles[1:]:
      articles[0]['search'] += a['search']
    results.append(articles[0])

  return results

# Create your models here.
class Narrative(models.Model):
  title = models.CharField(max_length=200)
  slug = models.SlugField()
  last_updated = models.DateTimeField()
  last_check = models.DateTimeField()
  next_check = models.DateTimeField()
  subscriptions = models.ManyToManyField(User)
  
  def searches(self):
    return GuardianSearch.objects.filter(narrative=self)

  def get_absolute_url(self):
    return reverse('narrative_slug', kwargs={'slug': self.slug})

  @property
  def results(self):
    rs = do_search(self)
    if len(rs) != 0:
      self.last_updated = rs[0]['date']
      self.save()
    return rs

  def populate_articles(self):
    Article.objects.filter(narrative=self).delete() # Trash existing articles in the db for this narrative
    for a in self.results:
      Article.objects.create(narrative=self,
                             headline=a['data']['webTitle'],
                             quote=a['firstpara'],
                             date=a['date'],
                             url=a['data']['webUrl'],
                             data=json.dumps(a['data']))

  def __unicode__(self):
    return self.title

class ReadTo(models.Model):
  user = models.ForeignKey(User)
  narrative = models.ForeignKey(Narrative)
  date = models.DateTimeField()

class Article(models.Model):
  headline = models.CharField(max_length=256)
  quote = models.TextField()
  date = models.DateTimeField()
  url = models.CharField(max_length=2048)
  data = models.TextField()

  narrative = models.ForeignKey(Narrative)

  def __unicode__(self):
    return self.headline 

class GuardianSearch(models.Model):
  narrative = models.ForeignKey(Narrative)
  term = models.TextField()
  tags = models.TextField()
  cache = models.TextField(blank=True)
 
  def __unicode__(self):
    return "%s - %s %s" % (self.narrative, self.term, self.tags)

  def do(self):
    if hasattr(self, 'results'):
      return self.results
    elif self.cache != "":
      self.results = json.loads(self.cache)
      return self.results
    else:
      self.results = gu.search(self.term, self.tags)
      self.cache = json.dumps(self.results)
      self.save()
      return self.results

