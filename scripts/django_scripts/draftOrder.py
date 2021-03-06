#!/usr/bin/python

import django
import os
import sys
import HTMLParser, urllib2, re
import logging
from math import floor
from random import random

if "/var/www/django.bhp" not in sys.path:
	sys.path.append("/var/www/django/bhp")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bhp.settings")
django.setup()

from django.conf import settings
from hockeypool.models import *
from draft.models import *

logger = logging.getLogger(__name__)

players = Player.objects.all().order_by("id")
Draft_Pick.objects.all().delete()
draftOrder = []

while(1):
	num = floor(random()*len(players))
	if num not in draftOrder:
		draftOrder.append(num)
	if len(draftOrder) == 8:
		break

draftOrder = [5,7,4,6,8,9,2,11]
draftOrder = [2,4,1,3,5,6,0,7]

p = Pool.objects.get(pk=1)
r = Draft_Round.objects.filter(year_id=p.current_year_id).order_by("number")[0]
num = 1
for i in range(0,19):
	if i%2 == 0:
		for x in draftOrder:
			print x
			Draft_Pick.objects.create(player = players[int(x)], round_id=i+r.id, number=num)
			num += 1
	else:
		for x in reversed(draftOrder):
			Draft_Pick.objects.create(player = players[int(x)], round_id=i+r.id, number=num)
			num += 1
