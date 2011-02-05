# Create your views here.
import json
import urllib2
import xml.utils.iso8601 as iso8601
import lxml.html
import itertools
from datetime import datetime, date, timedelta

from django.shortcuts import render_to_response

from models import Narrative, GuardianSearch

def home(request):
  narratives = Narrative.objects.all()

  for narrative in narratives:
    narrative.last_updated = narrative.results[0]['date']
    narrative.last_article = narrative.results[0]

  narratives = sorted(narratives, key=lambda narrative: narrative.last_updated, reverse=True)

  return render_to_response('home.html', {'narratives': narratives})

def narrative(request, id=None, slug=None):
  narrative = None
  if id is not None:
    narrative = Narrative.objects.get(pk=id)
  if slug is not None:
    narrative = Narrative.objects.get(slug=slug)

  return render_to_response('narrative.html', {'narrative': narrative})
