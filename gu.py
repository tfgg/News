import urllib2
import json
from datetime import datetime

endpoint = "http://content.guardianapis.com"
key = "uct3rztj38km5gcnwaeqmk3z"

def get_json(url):
  response = urllib2.urlopen("%s/%s&api-key=%s" % (endpoint, url, key))
  return json.loads(response.read())['response']

def get_all_pages(url):
  results = []
  
  page = 1
  pages = 1
  while page <= pages:
    response = get_json(url + "&page-size=50&page=%d" % page)
    pages = response['pages']
    results += response['results']
    page += 1

  return results

def get_last(n):
  results = []

  page = 1
  pages = n/50+1
  while page <= pages:
    response = get_json("search?order-by=newest&show-tags=all&show-fields=all&format=json&page-size=%d&page=%d" % (50, page))
    results += response['results']
    page += 1

  return results[:n]

def get_article(id):
  url = "%s?format=json&show-tags=all&show-fields=all" % id
  return get_json(url)

def get_today(pages=None):
  today = datetime.now().strftime('%Y-%m-%d')
  url = "search?from-date=%s&to-date=%s&order-by=newest&show-tags=all&show-fields=all&format=json" % (today, today)
  return get_all_pages(url)

def search(term,tag):
  term = urllib2.quote(term)
  tag = urllib2.quote(tag)
  url = "search?q=%s&tag=%s&page-size=50&show-tags=all&show-fields=all&order-by=newest&format=json" % (term,tag)
  return get_all_pages(url)

