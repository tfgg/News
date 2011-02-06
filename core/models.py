import json
from datetime import datetime, date, timedelta
import xml.utils.iso8601 as iso8601
import lxml.html
import itertools

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
      article['date'] = datetime.fromtimestamp(iso8601.parse(article['webPublicationDate']))
      article['istoday'] = (date.today() == article['date'].date())
      article['thisweek'] = (article['date'].date() > date.today() - timedelta(7))
      article['search'] = [search]
      
      if 'fields' in article and 'body' in article['fields']:
        if article['fields']['body'] == '<!-- Redistribution rights for this field are unavailable -->' or len(article['fields']['body']) == 0:
          article['firstpara'] = ""
        else:
          article['firstpara'] = strip_html(article['fields']['body']).split('\n')[0]
    all_results += results
  all_results = sorted(all_results, key=lambda article: article['date'], reverse=True)

  # Remove duplicates
  results = []
  grouped = itertools.groupby(all_results, lambda article: article['id'])
  for group, articles in grouped:
    articles = list(articles)
    for article in articles[1:]:
      articles[0]['search'] += article['search']
    results.append(articles[0])

  return results

# Create your models here.
class Narrative(models.Model):
  title = models.CharField(max_length=200)
  slug = models.SlugField()
  
  def searches(self):
    return GuardianSearch.objects.filter(narrative=self)

  def get_absolute_url(self):
    return reverse('narrative_slug', kwargs={'slug': self.slug})

  @property
  def results(self):
    rs = do_search(self)
    return rs

  def __unicode__(self):
    return self.title

class GuardianSearch(models.Model):
  narrative = models.ForeignKey(Narrative)
  term = models.TextField()
  tags = models.TextField()
  cache = models.TextField(blank=True)
 
  def __unicode__(self):
    return "%s - %s %s" % (self.narrative, self.term, self.tags)

  def do(self):
    if hasattr(self, 'results'):
      print "Cache loaded"
      return self.results
    elif self.cache != "":
      print "Cached but not loaded %s %s" % (self.term, self.tags)
      self.results = json.loads(self.cache)
      return self.results
    else:
      print "Not cached, not loaded"
      self.results = gu.search(self.term, self.tags)
      self.cache = json.dumps(self.results)
      self.save()
      return self.results
