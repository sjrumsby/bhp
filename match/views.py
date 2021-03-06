import datetime, time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from hockeypool.models import *
from match.models import *

import logging
logger = logging.getLogger(__name__)

@login_required
def index(request):
        current_time = timezone.localtime(timezone.now())
        formed_date = "%s-%s-%s" % (current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2))
        pool = Pool.objects.get(pk=1)
        week = pool.current_week

        if week.number == 0:
                week = Week.objects.get(year=pool.current_year, number=1)

        match = Match.objects.filter(week = week)
        game_ids = []
        match_data = []

        for g in Game.objects.filter(date=formed_date).values_list('home_team', flat="True"):
                game_ids.append(g)
        for g in Game.objects.filter(date=formed_date).values_list('away_team', flat="True"):
                game_ids.append(g)

        if len(match) > 0:
                for m in match:
                        tmp_arr = { 'match' : m, 'home' : { 'score' : 0 }, 'away' : { 'score' : 0 } }
                        tmp_arr['home']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week=week).values_list('date', flat=True), player=m.home_player).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))
                        tmp_arr['away']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week=week).values_list('date', flat=True), player=m.away_player).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))
                        tmp_arr['home']['in_action'] = Activated_Team.objects.filter(player=m.home_player).exclude(position=6).filter(skater__hockey_team__in=game_ids).filter(week_id=week.id).count()
                        tmp_arr['away']['in_action'] = Activated_Team.objects.filter(player=m.away_player).exclude(position=6).filter(skater__hockey_team__in=game_ids).filter(week_id=week.id).count()

                        if tmp_arr['home']['category_points']['fantasy_points'] > tmp_arr['away']['category_points']['fantasy_points']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 2
                        elif tmp_arr['home']['category_points']['fantasy_points'] < tmp_arr['away']['category_points']['fantasy_points']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 2

                        if tmp_arr['home']['category_points']['goals'] > tmp_arr['away']['category_points']['goals']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['goals'] < tmp_arr['away']['category_points']['goals']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['assists'] > tmp_arr['away']['category_points']['assists']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['assists'] < tmp_arr['away']['category_points']['assists']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['plus_minus'] > tmp_arr['away']['category_points']['plus_minus']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['plus_minus'] < tmp_arr['away']['category_points']['plus_minus']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['offensive_special'] > tmp_arr['away']['category_points']['offensive_special']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['offensive_special'] < tmp_arr['away']['category_points']['offensive_special']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['true_grit'] > tmp_arr['away']['category_points']['true_grit']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['true_grit'] < tmp_arr['away']['category_points']['true_grit']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['goalie'] > tmp_arr['away']['category_points']['goalie']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['goalie'] < tmp_arr['away']['category_points']['goalie']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1
                        if tmp_arr['home']['score'] == tmp_arr['away']['score']:
                                if tmp_arr['home']['category_points']['shootout'] > tmp_arr['away']['category_points']['shootout']:
                                        tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                                elif tmp_arr['home']['category_points']['shootout'] < tmp_arr['away']['category_points']['shootout']:
                                        tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        match_data.append(tmp_arr)
                context = {'page_name' : 'Schedule', 'state' : 1, 'matches' : match_data}
        else:
                context = {'page_name' : 'Schedule', 'state' : 0 }
        
        year = pool.current_year.description
        weeks = []
        if year != 20162017:
            for i in range (1,26):
                if i < 23:
                    weeks.append({"number": i, "type": "regular", "display": i})
                if i == 23:
                    weeks.append({"number": i, "type": "playoff", "display": "Divisional Round"})
                if i == 24:
                    weeks.append({"number": i, "type": "playoff", "display": "Conference Championship"})
                if i == 25:
                    weeks.append({"number": i, "type": "playoff", "display": "League Championship"})
        else:
            for i in range (1,27):
                if i < 24:
                    weeks.append({"number": i, "type": "regular", "display": i})
                if i == 24:
                    weeks.append({"number": i, "type": "playoff", "display": "Divisional Round"})
                if i == 25:
                    weeks.append({"number": i, "type": "playoff", "display": "Conferance Championships"})
                if i == 26:
                    weeks.append({"number": i, "type": "playoff", "display": "League Championships"})

        context["weeks"] = weeks
                
        return render(request, 'match/match.html', context)

@login_required
def match_detail(request, match_id):
        current_time = datetime.datetime.now()
        formed_date = "%s-%s-%s" % (current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2))
        match = Match.objects.select_related().filter(id = match_id)

        p=Pool.objects.get(pk=1)
        current_week = p.current_week

        game_ids = []
        for g in Game.objects.filter(date=formed_date).values_list('home_team', flat="True"):
                game_ids.append(g)
        for g in Game.objects.filter(date=formed_date).values_list('away_team', flat="True"):
                game_ids.append(g)

        for g in game_ids:
            logger.info(g)

        if len(match) > 0:
                match = match[0]
                match_info = []
                week = match.week.number
                m_info = { 'match' : match, 'home' : { 'score' : 0, 'expected' : {'category_points' : {'fantasy_points' : 0, 'goals' : 0, 'assists' : 0, 'plus_minus' : 0, 'offensive_special' : 0, 'true_grit' : 0, 'goalie' : 0, 'shootout' : 0}, 'score' : 0 } }, 'away' : { 'score' : 0, 'expected' : {'category_points' : {'fantasy_points' : 0, 'goals' : 0, 'assists' : 0, 'plus_minus' : 0, 'offensive_special' : 0, 'true_grit' : 0, 'goalie' : 0, 'shootout' : 0}, 'score' : 0 } } }

                m_info['home']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number=week).filter(week__year=p.current_year).values_list('date', flat=True), player=match.home_player).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))
                m_info['away']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number=week).filter(week__year=p.current_year).values_list('date', flat=True), player=match.away_player).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))
                m_info['home']['in_action'] = Activated_Team.objects.filter(player=match.home_player).filter(week__year=p.current_year).filter(week__number=week).filter(skater__hockey_team__in=game_ids).count()
                m_info['away']['in_action'] = Activated_Team.objects.filter(player=match.away_player).filter(week__year=p.current_year).filter(week__number=week).filter(skater__hockey_team__in=game_ids).count()

                home_team = Activated_Team.objects.select_related().filter(player = match.home_player).filter(week__number=week).filter(week__year=p.current_year)
                home_team_ids = home_team.values_list('skater__hockey_team_id', flat=True)
                away_team = Activated_Team.objects.select_related().filter(player = match.away_player).filter(week__number=week).filter(week__year=p.current_year)
                away_team_ids = away_team.values_list('skater__hockey_team_id', flat=True)

                home_daily_action = []
                away_daily_action = []

                for x in Week_Date.objects.filter(week__number=week).filter(week__year_id=p.current_year_id):
                        home_daily_action.append(Activated_Team.objects.filter(player=match.home_player).exclude(position=6).filter(week__number=week).filter(week__year=p.current_year).filter(Q(skater__hockey_team__in=Game.objects.filter(date=x.date).values_list('home_team', flat="True")) | (Q(skater__hockey_team__in=Game.objects.filter(date=x.date).values_list('away_team', flat="True")))).count())
                        away_daily_action.append(Activated_Team.objects.filter(player=match.away_player).exclude(position=6).filter(week__number=week).filter(week__year=p.current_year).filter(Q(skater__hockey_team__in=Game.objects.filter(date=x.date).values_list('home_team', flat="True")) | (Q(skater__hockey_team__in=Game.objects.filter(date=x.date).values_list('away_team', flat="True")))).count())

                m_info['home']['daily_action'] = home_daily_action
                m_info['away']['daily_action'] = away_daily_action

                if m_info['home']['category_points']['fantasy_points'] > m_info['away']['category_points']['fantasy_points']:
                        m_info['home']['score'] = m_info['home']['score'] + 2
                elif m_info['home']['category_points']['fantasy_points'] <  m_info['away']['category_points']['fantasy_points']:
                        m_info['away']['score'] = m_info['away']['score'] + 2

                if m_info['home']['category_points']['goals'] > m_info['away']['category_points']['goals']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['goals'] <  m_info['away']['category_points']['goals']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['category_points']['assists'] > m_info['away']['category_points']['assists']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['assists'] <  m_info['away']['category_points']['assists']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['category_points']['plus_minus'] > m_info['away']['category_points']['plus_minus']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['plus_minus'] <  m_info['away']['category_points']['plus_minus']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['category_points']['offensive_special'] > m_info['away']['category_points']['offensive_special']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['offensive_special'] <  m_info['away']['category_points']['offensive_special']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['category_points']['true_grit'] > m_info['away']['category_points']['true_grit']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['true_grit'] <  m_info['away']['category_points']['true_grit']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['category_points']['goalie'] > m_info['away']['category_points']['goalie']:
                        m_info['home']['score'] = m_info['home']['score'] + 1
                elif m_info['home']['category_points']['goalie'] <  m_info['away']['category_points']['goalie']:
                        m_info['away']['score'] = m_info['away']['score'] + 1

                if m_info['home']['score'] == m_info['away']['score']:
                        if m_info['home']['category_points']['shootout'] > m_info['away']['category_points']['shootout']:
                                m_info['home']['score'] = m_info['home']['score'] + 1
                        elif m_info['home']['category_points']['shootout'] <  m_info['away']['category_points']['shootout']:
                                m_info['away']['score'] = m_info['away']['score'] + 1


                home_team_ids = home_team.values_list("skater_id", flat="True")
                m_info['home']['team'] = []

                for h in home_team:
                        tmp_dict = { 'skater' : h.skater, 'position' : h.position }
                        if h.skater.hockey_team.id in game_ids:
                                tmp_dict['active'] = 1
                        else:
                                tmp_dict['active'] = 0
                        tmp_dict['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number=week).filter(week__year=p.current_year).values_list('date', flat=True),point__skater=h.skater).aggregate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), shootout=Sum('point__shootout'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'))
                        tmp_dict['num_games'] = Game.objects.filter(date__in=Week_Date.objects.filter(week=match.week).values_list('date', flat="True")).filter(Q(home_team=h.skater.hockey_team)|Q(away_team=h.skater.hockey_team)).count()
                        m_info['home']['team'].append(tmp_dict)

                away_team_ids = away_team.values_list('skater_id', flat="True")
                m_info['away']['team'] = []

                for h in away_team:
                        tmp_dict = { 'skater' : h.skater, 'position' : h.position }
                        if h.skater.hockey_team.id in game_ids:
                                tmp_dict['active'] = 1
                        else:
                                tmp_dict['active'] = 0
                        tmp_dict['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number=week).filter(week__year=p.current_year).values_list('date', flat=True),point__skater=h.skater).aggregate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), shootout=Sum('point__shootout'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'))
                        tmp_dict['num_games'] = Game.objects.filter(date__in=Week_Date.objects.filter(week=match.week).values_list('date', flat="True")).filter(Q(home_team=h.skater.hockey_team)|Q(away_team=h.skater.hockey_team)).count()
                        m_info['away']['team'].append(tmp_dict)

#                home_expect = Team_Point.objects.filter(player=match.home_player).values('point__game_id').annotate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'), shootout=Sum('point__shootout'))
#                away_expect = Team_Point.objects.filter(player=match.away_player).values('point__game_id').annotate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'), shootout=Sum('point__shootout'))

                pool = Pool.objects.get(pk=1)
                week = pool.current_week.number
                start_week = max(0, week-3)
                end_week = max(week, match.week.number)
                week_length = end_week - start_week
                nums = range(0, end_week)

                home_expect = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number__in=range(start_week, end_week)).filter(week__year=p.current_year).values_list('date', flat=True)).filter(point__skater_id__in=home_team_ids).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))
                away_expect = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week__number__in=range(start_week, end_week)).filter(week__year=p.current_year).values_list('date', flat=True)).filter(point__skater_id__in=away_team_ids).aggregate(fantasy_points=Coalesce(Sum('point__fantasy_points'),0), goals=Coalesce(Sum('point__goals'),0), assists=Coalesce(Sum('point__assists'),0), shootout=Coalesce(Sum('point__shootout'),0), plus_minus=Coalesce(Sum('point__plus_minus'),0), offensive_special=Coalesce(Sum('point__offensive_special'),0), true_grit=Coalesce(Sum('point__true_grit_special'),0), goalie=Coalesce(Sum('point__goalie'),0))

                for x in ['fantasy_points', 'goals', 'assists', 'plus_minus', 'offensive_special', 'true_grit', 'goalie', 'shootout']:
                    if home_expect[x] == None:
                        home_expect[x] = 0
                    if away_expect[x] == None:
                        away_expect[x] = 0

                home_expect['fantasy_points'] /= week_length
                home_expect['goals'] /= week_length
                home_expect['assists'] /= week_length
                home_expect['plus_minus'] /= week_length
                home_expect['offensive_special'] /= week_length
                home_expect['true_grit'] /= week_length
                home_expect['goalie'] /= week_length
                home_expect['shootout'] /= week_length
                away_expect['fantasy_points'] /= week_length
                away_expect['goals'] /= week_length
                away_expect['assists'] /= week_length
                away_expect['plus_minus'] /= week_length
                away_expect['offensive_special'] /= week_length
                away_expect['true_grit'] /= week_length
                away_expect['goalie'] /= week_length
                away_expect['shootout'] /= week_length

                m_info['home']['expected'] = {'category_points': home_expect}
                m_info['home']['expected']['score'] = 0
                m_info['away']['expected'] = {'category_points': away_expect}
                m_info['away']['expected']['score'] = 0

                if m_info['home']['expected']['category_points']['fantasy_points'] > m_info['away']['expected']['category_points']['fantasy_points']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 2
                elif m_info['home']['expected']['category_points']['fantasy_points'] <  m_info['away']['expected']['category_points']['fantasy_points']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 2

                if m_info['home']['expected']['category_points']['goals'] > m_info['away']['expected']['category_points']['goals']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['goals'] <  m_info['away']['expected']['category_points']['goals']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['category_points']['assists'] > m_info['away']['expected']['category_points']['assists']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['assists'] <  m_info['away']['expected']['category_points']['assists']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['category_points']['plus_minus'] > m_info['away']['expected']['category_points']['plus_minus']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['plus_minus'] <  m_info['away']['expected']['category_points']['plus_minus']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['category_points']['offensive_special'] > m_info['away']['expected']['category_points']['offensive_special']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['offensive_special'] <  m_info['away']['expected']['category_points']['offensive_special']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['category_points']['true_grit'] > m_info['away']['expected']['category_points']['true_grit']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['true_grit'] <  m_info['away']['expected']['category_points']['true_grit']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['category_points']['goalie'] > m_info['away']['expected']['category_points']['goalie']:
                        m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                elif m_info['home']['expected']['category_points']['goalie'] <  m_info['away']['expected']['category_points']['goalie']:
                        m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1

                if m_info['home']['expected']['score'] == m_info['away']['expected']['score']:
                        if m_info['home']['expected']['category_points']['shootout'] > m_info['away']['expected']['category_points']['shootout']:
                                m_info['home']['expected']['score'] = m_info['home']['expected']['score'] + 1
                        elif m_info['home']['expected']['category_points']['shootout'] <  m_info['away']['expected']['category_points']['shootout']:
                                m_info['away']['expected']['score'] = m_info['away']['expected']['score'] + 1


        context = {'page_name' : 'Match: %s' % match_id, 'match' : m_info }
        return render(request, 'match/match_detail.html', context)

@login_required
def match_week(request, week_number):
        current_time = timezone.localtime(timezone.now())
        formed_date = "%s-%s-%s" % (current_time.year, str(current_time.month).zfill(2), str(current_time.day).zfill(2))
        pool = Pool.objects.get(pk=1)
        year_id = pool.current_year_id
        week = Week.objects.get(number=week_number, year_id=year_id)

        if week.number == 0:
                week = Week.objects.get(year=pool.current_year, number=1)

        match = Match.objects.filter(week = week)
        game_ids = []
        match_data = []

        for g in Game.objects.filter(date=formed_date).values_list('home_team', flat="True"):
                game_ids.append(g)
        for g in Game.objects.filter(date=formed_date).values_list('away_team', flat="True"):
                game_ids.append(g)

        if len(match) > 0:
                for m in match:
                        tmp_arr = { 'match' : m, 'home' : { 'score' : 0 }, 'away' : { 'score' : 0 } }
                        tmp_arr['home']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week=week).values_list('date', flat=True), player=m.home_player).aggregate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), shootout=Sum('point__shootout'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'))
                        tmp_arr['away']['category_points'] = Team_Point.objects.filter(point__game__date__in = Week_Date.objects.filter(week=week).values_list('date', flat=True), player=m.away_player).aggregate(fantasy_points=Sum('point__fantasy_points'), goals=Sum('point__goals'), assists=Sum('point__assists'), shootout=Sum('point__shootout'), plus_minus=Sum('point__plus_minus'), offensive_special=Sum('point__offensive_special'), true_grit=Sum('point__true_grit_special'), goalie=Sum('point__goalie'))
                        tmp_arr['home']['in_action'] = Activated_Team.objects.filter(player=m.home_player).exclude(position=6).filter(skater__hockey_team__in=game_ids).filter(week_id=week.id).count()
                        tmp_arr['away']['in_action'] = Activated_Team.objects.filter(player=m.away_player).exclude(position=6).filter(skater__hockey_team__in=game_ids).filter(week_id=week.id).count()

                        if tmp_arr['home']['category_points']['fantasy_points'] > tmp_arr['away']['category_points']['fantasy_points']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 2
                        elif tmp_arr['home']['category_points']['fantasy_points'] < tmp_arr['away']['category_points']['fantasy_points']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 2

                        if tmp_arr['home']['category_points']['goals'] > tmp_arr['away']['category_points']['goals']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['goals'] < tmp_arr['away']['category_points']['goals']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['assists'] > tmp_arr['away']['category_points']['assists']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['assists'] < tmp_arr['away']['category_points']['assists']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['plus_minus'] > tmp_arr['away']['category_points']['plus_minus']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['plus_minus'] < tmp_arr['away']['category_points']['plus_minus']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['offensive_special'] > tmp_arr['away']['category_points']['offensive_special']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['offensive_special'] < tmp_arr['away']['category_points']['offensive_special']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['true_grit'] > tmp_arr['away']['category_points']['true_grit']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['true_grit'] < tmp_arr['away']['category_points']['true_grit']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        if tmp_arr['home']['category_points']['goalie'] > tmp_arr['away']['category_points']['goalie']:
                                tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                        elif tmp_arr['home']['category_points']['goalie'] < tmp_arr['away']['category_points']['goalie']:
                                tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1
                        if tmp_arr['home']['score'] == tmp_arr['away']['score']:
                                if tmp_arr['home']['category_points']['shootout'] > tmp_arr['away']['category_points']['shootout']:
                                        tmp_arr['home']['score'] = tmp_arr['home']['score'] + 1
                                elif tmp_arr['home']['category_points']['shootout'] < tmp_arr['away']['category_points']['shootout']:
                                        tmp_arr['away']['score'] = tmp_arr['away']['score'] + 1

                        match_data.append(tmp_arr)
                context = {'page_name' : 'Schedule', 'state' : 1, 'matches' : match_data}
        else:
                context = {'page_name' : 'Schedule', 'state' : 0 }
        
        year = pool.current_year.description
        weeks = []
        if year != 20162017:
            for i in range (1,26):
                if i < 23:
                    weeks.append({"number": i, "type": "regular", "display": i})
                if i == 23:
                    weeks.append({"number": i, "type": "playoff", "display": "Divisional Round"})
                if i == 24:
                    weeks.append({"number": i, "type": "playoff", "display": "Conference Championship"})
                if i == 25:
                    weeks.append({"number": i, "type": "playoff", "display": "League Championship"})
        else:
            for i in range (1,27):
                if i < 24:
                    weeks.append({"number": i, "type": "regular", "display": i})
                if i == 24:
                    weeks.append({"number": i, "type": "playoff", "display": "Divisional Round"})
                if i == 25:
                    weeks.append({"number": i, "type": "playoff", "display": "Conferance Championships"})
                if i == 26:
                    weeks.append({"number": i, "type": "playoff", "display": "League Championships"})

        context["weeks"] = weeks
                
        return render(request, 'match/match.html', context)

@login_required
def match_activate(request):
    activations = Activation.objects.filter(player__id = request.user.id)
    team = Team.objects.filter(player__id = request.user.id)
    team_array = []
    pool = Pool.objects.get(pk=1)
    for t in team:
        date = datetime.datetime.now()
        formed_date = "%s-%s-%s" % (date.year, str(date.month).zfill(2), str(date.day).zfill(2))
        current_week = pool.current_week
        next_week = current_week.number + 1
        tmp_arr = {'skater' : t}
        check = 0
        position = 0

        for x in activations:
            if t.skater.nhl_id == x.skater.nhl_id:
                check = 1
                position = x.position

        tmp_arr['check'] = check

        if position != 0:
            tmp_arr['position'] = str(position)
        else:
            tmp_arr['position'] = 'X'

        tmp_arr['positions'] = [str(a) for a in t.skater.get_position()]
        if ',' in tmp_arr['positions']:
            tmp_arr['positions'].remove(',')
        if ' ' in tmp_arr['positions']:
            tmp_arr['positions'].remove(' ')

        tmp_arr['category_points'] = Point.objects.filter(skater = t.skater).filter(game__year_id=pool.current_year_id).aggregate(fantasy_points=Sum('fantasy_points'), goals=Sum('goals'), assists=Sum('assists'), shootout=Sum('shootout'), plus_minus=Sum('plus_minus'), offensive_special=Sum('offensive_special'), true_grit=Sum('true_grit_special'), goalie=Sum('goalie'))
        tmp_arr['num_games'] = Game.objects.filter(date__in=Week_Date.objects.filter(week__number=next_week).filter(week__year_id=pool.current_year_id).values_list('date', flat="True")).filter(Q(home_team=t.skater.hockey_team)|Q(away_team=t.skater.hockey_team)).count()
        team_array.append(tmp_arr)

    context = {'page_name' : 'Activate', 'team' : team_array}
    return render(request, 'match/match_activate.html', context)

