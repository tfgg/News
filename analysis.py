# -*- coding: utf-8 -*-
from datetime import datetime
import re
import json
import os, os.path, sys
import lxml.html
import sqlite3
import xml.utils.iso8601 as iso8601
import operator
import gu
import math
from collections import Counter

remove_chars = [':', '-', ',', '\'', '|', '.', ';', '"', '(', ')', '?', '[', ']', '{', '}']

def strip(s):
  for c in remove_chars:
    s = s.replace(c, " ")
  return s.lower()

def strip_html(s):
  s = re.sub('<.*?>', ' ', s)
  return s

def clean(s):
  s = re.sub('<.*?>', ' ', s)
  s = re.sub('[0-9]+', ' ', s)
  for c in remove_chars: 
    s = s.replace(c, " ")
  
  try:
    t = lxml.html.fromstring(s)
    return t.text_content()
  except lxml.etree.ParserError:
    return s

words = {}
num_words = 0

tags = {}
num_tags = 0

def load_word_corpus():
  print "Loading 1-gram corpus..."
  if os.path.isfile("ngram/merged.json"):
    words = json.load(open("ngram/merged.json"))

  print "Loading tag corpus..."
  if os.path.isfile("tags.json"):
    tags = json.load(open("tags.json"))

  print "Counting words..."
  num_words = sum([v for k,v in words.items()])
  num_tags = sum([v for k,v in tags.items()])

  print "Done."

def score(word, count):
  if word in words:
    return math.log10(float(count) / (float(words[word])/num_words))
  else:
    return None

if os.path.isfile(sys.argv[1]):
  words_in = open(sys.argv[1]).read().split()
else:
  words_in = sys.argv[1:]

def get_or_zero(x,d):
  if x in d: return float(d[x])
  else: return 0.0

def generate_search(story):
  headline = story['webTitle']
  body = clean(story['fields']['body'])
  article_tags = [tag['id'] for tag in story['tags']]
  
  headline_counted = Counter(headline.split()).items()
  body_counted = Counter(body.split()).items()

  word_score = [(word, score(word, count)) for word, count in headline_counted if score(word, count) is not None]
  word_score = sorted([(k,v) for k,v in word_score], key=lambda (k,v): v, reverse=True)

  body_score = [(word, score(word, count)) for word, count in body_counted if score(word, count) is not None]
  body_score = sorted([(k,v) for k,v in body_score], key=lambda (k,v): v, reverse=True)

  tag_score = [(tag, get_or_zero(tag, tags)) for tag in article_tags]
  tag_score = sorted(tag_score, key=lambda (t,v): v)

  print word_score
  print body_score
  print tag_score

  searches = []

  searches.append((' '.join([k for k,v in word_score][:2]), ','.join(tag_score[:1][0] + ['tone/news'])))
  
  return (word_score, searches)

if len(sys.argv) < 1:
  print "Possible actions: add"
elif sys.argv[1] == 'analyse':
  load_word_corpus()
  story_id = sys.argv[2]
  story = gu.get_article(story_id)['content']
  
  word_score, searches = generate_search(story)
 
  print searches

  word_count = {} 
  
  for search_term, search_tags in searches:
    print search_term, search_tags
elif sys.argv[1] == 'today':
  load_word_corpus()
  articles = gu.get_today()

  for article in articles:
    print article['webTitle']
    ws, ts, searches = generate_search(article)

    for term, tags in searches:
      print "  ", term, tags
elif sys.argv[1] == 'source':
  articles = gu.get_today()

  phrases = {'parl_vote': ['the vote', 'defeated in the commons', 'mps voted'],
             'press_release': ['according to a study', 'a study', 'a study showed', 'scientists say',],}

  for article in articles:
    print article['webTitle']
    if 'fields' not in article or 'body' not in article['fields']:
      continue
    text = strip(article['fields']['body'])

    for phrase in phrases:
      if phrase in text:
        print phrase
