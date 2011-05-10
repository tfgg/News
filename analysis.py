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
import ner
import common
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

def load_tag_corpus():
  print "Loading tag corpus..."
  if os.path.isfile("tags.json"):
    print "Found tags file"
    tags = json.load(open("tags.json"))

  num_tags = sum([v for k,v in tags.items()])

  return tags

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
  
  return (word_score, tag_score, searches)

def score_tags(tags, article_tags):
  def inv_or_def(x, d):
    if x == 0.0:
      return d
    else:
      return 1.0/x
  tag_score = [(tag, inv_or_def(get_or_zero(tag, tags),1e4)) for tag in article_tags if 'profile/' not in tag]
  tag_score = sorted(tag_score, key=lambda (t,v): v)

  return tag_score

def get_tags(article):
  return [tag['id'] for tag in article['tags']]
   

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
  tags = load_tag_corpus()
  articles = gu.get_last(int(sys.argv[2]))

  print "Got %d articles" % (len(articles))

  tagged_articles = []
  for article in articles:
    print "Analysing %s" % (article['webTitle'])
    ts = set(score_tags(tags, get_tags(article)))
    ts = set()
    if 'fields' in article and 'body' in article['fields']:
      things = ner.process_string(clean(article['fields']['body']))
      found_entities = [thing for thing in things if thing.entity_type in ['proper_noun', 'initialism', 'acryonym', 'thing']]

      entities = set()
      for entity in found_entities:
        if entity.entity_type == 'thing':
          entities.add(entity.string)
        elif entity.entity_type == 'proper_noun':
          if entity.value.lower() not in common.english:
            entities.add(entity.value)
        else:
          entities.add(entity.value)

      #print map(str, found_entities)

      if 'Redistribution' in entities and len(entities) == 1:
        entities = set()
      #print entities
    else:
      entities = set()
    
    if len(entities) != 0 and 'tone/news' in get_tags(article) and ' - video' not in article['webTitle']:
      tagged_articles.append((ts, entities, article))

  common = {}
  related = {}
  for ts1, es1,a1 in tagged_articles:
    for ts2, es2, a2 in tagged_articles:
      if a1 is a2:
        continue
      
      overlap_tags = ts1 & ts2
      overlap_entities = es1 & es2

      for entity in overlap_entities:
        if entity in related:
          related[entity].add(a1['id'])
          related[entity].add(a2['id'])
        else:
          related[entity] = set([a1['id'], a2['id']])

      total1 = sum([score for tag, score in ts1]) + sum([0.01 for v in es1])
      total2 = sum([score for tag, score in ts2]) + sum([0.01 for v in es2])
      total = total1 + total2
      overlap_score = (sum([score for tag, score in overlap_tags]) + sum([0.01 for v in overlap_entities])) * 2.0
      score = overlap_score / total

      if score > 0.15 and a1 is not a2:
        print "%f | %s | %s | %s" % (score, a1['webTitle'], a2['webTitle'], str(overlap_entities))
  
  related_size = [(entity, len(s)) for entity, s in related.items()]
  print sorted(related_size, key=lambda (x,y): y)
  print related

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
elif sys.argv[1] == 'common':
  tags = load_tag_corpus()
  # Given a set of articles, work out the search terms.
  article_ids = sys.argv[2:]

  articles = [gu.get_article(id)['content'] for id in article_ids]

  common_tags = None
  tag_freq = Counter()
  for article in articles:
    article_tags = set([tag['id'] for tag in article['tags'] if 'profile/' not in tag['id']])
    for tag in article_tags:
      tag_freq[tag] += 1
    if common_tags is None:
      common_tags = article_tags
    common_tags =  article_tags & common_tags

  def default(d,v,df):
    if v in d: return d[v]
    else: return df

  print common_tags
  sorted_tags = sorted([(tag, freq, default(tags, tag, 0), float(freq)/default(tags, tag, 0)) for tag, freq in tag_freq.items()], key=lambda x: x[3])
  for tag, freq_article, freq_pop, score in sorted_tags:
    print tag, freq_article, freq_pop, math.log10(score)

