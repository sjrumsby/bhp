#!/usr/bin/python

import django
import os
import sys
import HTMLParser, urllib2, re, time, json
import logging

if "/var/www/django.bhp" not in sys.path:
	sys.path.append("/var/www/django/bhp")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bhp.settings")
django.setup()

from django.conf import settings
from hockeypool.models import *

teams = {
		"Anaheim Ducks": "Anaheim",
		"Arizona Coyotes":"Arizona",
		"Boston Bruins":"Boston",
		"Buffalo Sabres":"Buffalo",
		"Calgary Flames":"Calgary",
		"Carolina Hurricanes":"Carolina",
		"Chicago Blackhawks":"Chicago",
		"Colorado Avalanche":"Colorado",
		"Columbus Blue Jackets":"Columbus",
		"Dallas Stars":"Dallas",
		"Detroit Red Wings":"Detroit",
		"Edmonton Oilers":"Edmonton",
		"Florida Panthers":"Florida",
		"Los Angeles Kings":"Los Angeles",
		"Minnesota Wild": "Minnesota",
		"Montreal Canadiens":"Montreal",
		u"Montr\xe9al Canadiens":"Montreal",
		"Nashville Predators":"Nashville",
		"New Jersey Devils":"New Jersey",
		"NY Rangers":"NY Rangers",
		"New York Rangers":"NY Rangers",
		"NY Islanders":"NY Islanders",
		"New York Islanders":"NY Islanders",
		"Ottawa Senators":"Ottawa" ,
		"Philadelphia Flyers":"Philadelphia",
		"Pittsburgh Penguins":"Pittsburgh",
		"San Jose Sharks":"San Jose",
		"St. Louis Blues":"St. Louis",
		"Toronto Maple Leafs":"Toronto",
		"Tampa Bay Lightning":"Tampa Bay",
		"Vancouver Canucks":"Vancouver",
		"Washington Capitals":"Washington",
		"Winnipeg Jets": "Winnipeg"
	}
p = Pool.objects.get(pk=1)
weeks = Week.objects.filter(year_id=p.current_year_id).filter(number__gt=0)

week_dates = Week_Date.objects.filter(week_id__in=weeks.values_list('id', flat=True))

for w in week_dates:
	uri = "http://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s" % (w.date, w.date)
	response = urllib2.urlopen(uri)
	data = response.read()
	jsonData = json.loads(data)
	if len(jsonData["dates"]) == 0:
		continue
	for g in jsonData["dates"][0]["games"]:
		awayTeamName =  teams[g["teams"]["away"]["team"]["name"]]
		homeTeamName =  teams[g["teams"]["home"]["team"]["name"]]
		
		awayTeam = Hockey_Team.objects.get(full_name=awayTeamName)
		homeTeam = Hockey_Team.objects.get(full_name=homeTeamName)
		nhl_game_id = g["gamePk"]

		print "%s (%s @ %s)" % (nhl_game_id, awayTeam, homeTeam)
		g = Game.objects.filter(nhl_game_id=nhl_game_id)

		if len(g) == 0:
			print "Adding game: %s" % nhl_game_id
#			Game.objects.create(date=w.date, home_team=homeTeam, away_team=awayTeam, nhl_game_id=g["gamePk"], year_id=p.current_year_id, time="00:00:00")
		else:
			print "Game already exists: %s" % nhl_game_id




