from pyramid.response import Response
from pyramid.view import view_config,view_defaults
import random
import math
from pyramid.httpexceptions import (
HTTPFound,
HTTPNotFound,
)
import re
from sqlalchemy.exc import DBAPIError
from ..models import *
def gold_sort_tables(dict):
    list = []
    ex = None
    for t in dict.items():
        try:
            if int(t[0].number):
                list.append(t)
        except:
            ex = t
    list.sort(key=lambda x: int(x[0].number))
    if ex:
        list.append(ex)
    return list

def gold_sort_dict(dict):
    list = []
    ex = None
    for t in dict.items():
        try:
            if int(t[0]):
                list.append(t)
        except:
            ex = t
    list.sort(key=lambda x: int(x[0]))
    if ex:
        list.append(ex)
    return list

def gold_sort_list(dict):
    list = []
    ex = None
    for t in dict:
        try:
            if int(t.weight):
                list.append(t)
        except:
            ex = t
    list.sort(key=lambda x: int(x.weight))
    if ex:
        list.append(ex)
    return list

def first_tour(event,hand):
    tournaments = DBSession.query(Tournament).filter_by(event=event,hand=hand)
    for tournament in tournaments:
        #Все участники
        players = tournament.players
        #Количество участников
        number_players = len(players)
        #Количество участников в 1 туре
        number_players_1tour = 0

        if hand:
            players.sort(key=lambda x: int(x.right_hand))
        else:
            players.sort(key=lambda x: int(x.left_hand))

        i=0
        while(i<number_players):
            if 2**i >= number_players:
                number_players_1tour = 2**i
                break
            i+=1

        number_games_in_tour = number_players_1tour / 2


        #Туры в сетке виннеров
        tour_win = 1
        # Туры в сетке лузеров
        tour_lose = 1
        #Количество халявщиков
        dif = number_players_1tour - number_players
        #Количество пар в первом туре
        pare = (number_players - dif)/2
        #Индексы для игроков
        l = 0
        #Создание всех туров сетки и заполнение 1 тура
        while(number_games_in_tour>0):
            k = 0
            while(k<number_games_in_tour):
                if tour_win == 1:
                    if pare>0:
                        win_grid = WinGrid(tour=tour_win, tournament=tournament)
                        DBSession.add(win_grid)
                        win_grid.games.append(players[l])
                        win_grid.games.append(players[l+1])
                        l+=2
                        pare-=1
                    else:
                        win_grid = WinGrid(tour=tour_win, tournament=tournament,winner=players[l])
                        DBSession.add(win_grid)
                        l+=1
                else:
                    win_grid = WinGrid(tour=tour_win, tournament=tournament)
                    lose_grid1 = LoseGrid(tour=tour_lose, tournament=tournament)
                    lose_grid2 = LoseGrid(tour=tour_lose+1, tournament=tournament)
                    DBSession.add_all([win_grid,lose_grid1,lose_grid2])
                k += 1

            number_games_in_tour//=2
            if tour_win !=1:
                tour_lose += 2
            tour_win+=1

def tournaments_for_player(tournaments_left,tournaments_right,weight):
    list = []

    tournaments_left = gold_sort_list(tournaments_left)
    for t in tournaments_left:
        try:
            if weight <= int(t.weight):
                list.append(t)
                break
        except:
            list.append(t)

    tournaments_right = gold_sort_list(tournaments_right)
    for t in tournaments_right:
        try:
            if weight <= int(t.weight):
                list.append(t)
                break
        except:
            list.append(t)
    return list

@view_config(route_name='all_tournaments', renderer='templates/allTournaments.jinja2')
@view_config(route_name='api_all_tournaments', renderer='myjson')
def at_view(request):
    events = DBSession.query(Event).filter_by().all()
    if request.matched_route.name == 'api_all_tournaments':
        list = []
        for event in events:
            list.append({
                "id":event.id,
                "number_tables":event.numberTable,
                "name":event.name,
                "city":event.city,
                "date":event.date,
                "date_end":event.dateEnd,
                "description":event.description,
                "building":event.building,
                "address":event.address,
                "user_id":event.userId,
                "type_id":event.typeId
            })
        return {
            'events':list
        }
    return{
        'events':events
    }


@view_config(route_name='my_tournaments', renderer='templates/myTournaments.jinja2',permission = "view")
@view_config(route_name='api_my_tournaments', renderer='myjson')
def mt_view(request):
    user = DBSession.query(User).filter_by(login=request.authenticated_userid).first()
    events = user.events if user else ""
    if request.matched_route.name == 'api_my_tournaments':
        list = []
        for event in events:
            list.append({
                "id": event.id,
                "number_tables": event.numberTable,
                "name": event.name,
                "city": event.city,
                "date": event.date,
                "date_end": event.dateEnd,
                "description": event.description,
                "building": event.building,
                "address": event.address,
                "user_id": event.userId,
                "type_id": event.typeId
            })
        return {
            'events': list
        }
    return {'events':events}

@view_config(route_name='new_tournament', renderer='templates/newTournament.jinja2',permission = "view")
@view_config(route_name='api_new_tournament', renderer='myjson')
def nt_view(request):
    if request.matched_route.name == 'api_new_tournament' and 'name' in request.params:
        name = request.params['name']
        e = DBSession.query(Event).filter_by(name=name).all()[-1]
        return {
            "event_id": e.id
        }
    if 'submitted' in request.params:
        user = DBSession.query(User).filter_by(login=request.authenticated_userid).first()


        if 'type' in request.params:
            typeName = request.params['type']
        else:
            return HTTPFound(location='/new_tournament')

        type = DBSession.query(Type).filter_by(name=typeName).first()

        if 'number_table' in request.params:
            number_table = request.params['number_table']
        else:
            return HTTPFound(location='/new_tournament')

        if 'name' in request.params:
            name = request.params['name']
        else:
            return HTTPFound(location='/new_tournament')


        if 'date' in request.params:
            date = request.params['date']
            if date != "":
                d = date.split('-')
                date = d[2] + "." + d[1] + "." + d[0]
        else:
            date = ""

        if 'date2' in request.params:
            date2 = request.params['date2']
            if date2 != "":
                d = date2.split('-')
                date2 = d[2] + "." + d[1] + "." + d[0]
        else:
            date2 = ""

        weight_man = request.params['weight_man'] if 'weight_man' in request.params else ""
        weight_woman = request.params['weight_woman'] if 'weight_woman' in request.params else ""
        city = request.params['city'] if 'city' in request.params else ""
        description = request.params['description'] if 'description' in request.params else ""
        building = request.params['build'] if 'build' in request.params else ""
        address = request.params['address'] if 'address' in request.params else ""

        event = Event(numberTable=number_table,name=name,city=city,date=date,dateEnd=date2,
                      description=description,building=building,address=address,user=user,type=type)
        DBSession.add(event)

        if weight_man and weight_woman:
            weight_man = weight_man.split(',')
            type = DBSession.query(Type).filter_by(id=2).first()

            for weight in weight_man:
                if weight != "":
                    t = Tournament(hand=0, event=event, type=type, weight=weight)
                    t2 = Tournament(hand=1, event=event, type=type, weight=weight)
                    DBSession.add_all([t,t2])

            weight_woman = weight_woman.split(',')
            type = DBSession.query(Type).filter_by(id=1).first()
            for weight in weight_woman:
                if weight != "":
                    t = Tournament(hand=0, event=event, type=type, weight=weight)
                    t2 = Tournament(hand=1, event=event, type=type, weight=weight)
                    DBSession.add_all([t,t2])
        else:
            if weight_man:
                type = DBSession.query(Type).filter_by(id=2).first()
                weight_man = weight_man.split(',')
                for weight in weight_man:
                    if weight != "":
                        t = Tournament(hand=0,event=event,type=type,weight=weight)
                        t2 = Tournament(hand=1, event=event, type=type, weight=weight)
                        DBSession.add_all([t,t2])

            if weight_woman:
                type = DBSession.query(Type).filter_by(id=1).first()
                weight_woman = weight_woman.split(',')
                for weight in weight_woman:
                    if weight != "":
                        t = Tournament(hand=0, event=event, type=type, weight=weight)
                        t2 = Tournament(hand=1, event=event, type=type, weight=weight)
                        DBSession.add_all([t,t2])


        return HTTPFound(location='/my_tournaments')
    return {}

@view_config(route_name='tournament_detail', renderer='templates/tournamentDetail.jinja2')
@view_config(route_name='api_tournament_detail', renderer='myjson')
def td_view(request):
    id = request.matchdict['name']
    event = DBSession.query(Event).filter_by(id=id).first()
    if event:
        #Количество столов
        tables_number = event.numberTable

        #Получение всех турниров мероприятия
        tournaments = event.tournaments

        #Проверка на начало турниров
        start = False

        #Словари для распределения участников по весовым категориям
        #Заполнение данными словарей с участниками турнира
        for tournament in tournaments:
            if tournament.win_grids:
                start = True

        dict_tournaments_woman = {tournament.weight:tournament.players for tournament in tournaments if tournament.hand and tournament.typeId == 1}
        dict_tournaments_man = {tournament.weight:tournament.players for tournament in tournaments if tournament.hand and tournament.typeId == 2}

        #Упорядочивание по весовым категориям
        list_tournaments_man = gold_sort_dict(dict_tournaments_man)
        list_tournaments_woman = gold_sort_dict(dict_tournaments_woman)

        #Не стартовавшее мероприятие
        if not start:
            if 'start' in request.params:
                first_tour(event,0)
                first_tour(event,1)
                return HTTPFound(location="/tournament/"+str(event.id))

            if request.matched_route.name == 'api_tournament_detail':
                list = []

                for tournament in tournaments:
                    players = []
                    for player in tournament.players:
                        players.append({
                            "id": player.id,
                            "first_name": player.first_name,
                            "middle_name": player.middle_name,
                            "last_name": player.last_name,
                            "age": player.age,
                            "sex": player.sex,
                            "weight": player.weight,
                            "team": player.team,
                            "event_id": player.eventId
                        })

                    list.append({
                        "id": tournament.id,
                        "hand": tournament.hand,
                        "type_id": tournament.typeId,
                        "weight": tournament.weight,
                        "players": players
                    })
                return {
                    "tournaments": list
                }

            if 'settings' in request.params:
                if 'age' in request.params:
                    age = request.params['age']
                    if age != "":
                        d = age.split('-')
                        age = d[2] + "." + d[1] + "." + d[0]
                else:
                    age = ""
                first_name = request.params['first_name'] if 'first_name' in request.params else ""
                middle_name = request.params['middle_name'] if 'middle_name' in request.params else ""
                last_name = request.params['last_name'] if 'last_name' in request.params else ""
                sex = request.params['sex']
                sex = 0 if sex == "Женщина" else 1
                if 'weight' in request.params:
                    weight = float(request.params['weight'])
                else:
                    return {"event":event,
                            "dict_tournaments_man": list_tournaments_man,
                            "dict_tournaments_woman": list_tournaments_woman,
                            "message":"Вес неверен"}
                team = request.params['team'] if 'team' in request.params else ""
                random_left = random.randint(1,1000)
                random_right = random.randint(1,1000)

                if sex:
                    #type = DBSession.query(Type).filter_by(id=2).first()
                    ts_left = DBSession.query(Tournament).filter_by(typeId=2,hand=0,event=event).all()
                    ts_right = DBSession.query(Tournament).filter_by(typeId=2,hand=1,event=event).all()
                    player_tournaments = tournaments_for_player(ts_left,ts_right,weight)
                else:
                    #type = DBSession.query(Type).filter_by(id=1).first()
                    ts_left = DBSession.query(Tournament).filter_by(typeId=1, hand=0, event=event).all()
                    ts_right = DBSession.query(Tournament).filter_by(typeId=1, hand=1, event=event).all()
                    player_tournaments = tournaments_for_player(ts_left, ts_right, weight)

                if not player_tournaments:
                    return {"event":event,
                            "dict_tournaments_man": list_tournaments_man,
                            "dict_tournaments_woman": list_tournaments_woman,
                            "message":"Нет турнира для этого участника"}
                player = Player(first_name=first_name,middle_name=middle_name,last_name=last_name,left_hand=random_left,
                                     right_hand=random_right,age=age,sex=sex,weight=weight,team=team,event=event)
                DBSession.add(player)
                for tournament in player_tournaments:
                    tournament.players.append(player)
                return HTTPFound(location="/tournament/"+str(event.id))

            return {"event":event,
                    "dict_tournaments_man":list_tournaments_man,
                    "dict_tournaments_woman":list_tournaments_woman}

        #Стартовавшее мероприятие
        dict_table = {}
        tables = event.tables

        # Создание столов
        if not tables:
            i = 0
            while (i < tables_number):
                t = Table(number=i + 1, event=event, tournament=tournaments[0])
                DBSession.add(t)
                i += 1

        # Вывод турниров на столы
        for table in tables:
            if str(table.number) in request.params:
                if 'weight_tournament' in request.params:
                    weight = request.params['weight_tournament']
                    type = DBSession.query(Type).filter_by(id=1).first() if 'Ж' in weight else DBSession.query(Type).filter_by(id=2).first()
                    if 'правая' in weight:
                        t = DBSession.query(Tournament).filter_by(event=event, weight=weight.split('к')[0][2:],hand=1,type=type).first()
                        table.tournament = t
                    else:
                        t = DBSession.query(Tournament).filter_by(event=event, weight=weight.split('к')[0][2:],hand=0,type=type).first()
                        table.tournament = t

            games = []
            for w in table.tournament.win_grids:
                full_list = []
                if not w.winnerId and len(w.games)>0:
                    for l in w.games:
                        full_name = l.middle_name + " " + l.first_name
                        full_list.append(full_name)
                    games.append(full_list)
                    dict_table[table] = games
                else:
                    dict_table[table] = []

            for w in table.tournament.lose_grids:
                full_list = []
                if not w.winnerId and len(w.games)>0:
                    for l in w.games:

                        full_name = l.middle_name + " " + l.first_name
                        full_list.append(full_name)
                    games.append(full_list)
                    dict_table[table] = games
                else:
                    dict_table[table] = games

        list_table = gold_sort_tables(dict_table)

        # Определение победителя в каком-либо матче
        if 'confirm' in request.params :
            winner = request.params['winner'] if 'winner' in request.params else ""
            split_winner = winner.split(' ')
            if winner:
                first_name = split_winner[2]
                middle_name = split_winner[1]
                weight = split_winner[4][:-2]
                hand = split_winner[5]
                hand = False if hand == '(левая)' else True
                type = split_winner[3]
                type = DBSession.query(Type).filter_by(id=1).first() if type == 'Ж' else DBSession.query(Type).filter_by(id=2).first()
                tournament = DBSession.query(Tournament).filter_by(event=event,hand=hand,weight=weight,type=type).first()
                player_win = DBSession.query(Player).filter_by(event=event,first_name=first_name,middle_name=middle_name).first()

                for w in tournament.win_grids:
                    if not w.winnerId:
                        if player_win in w.games:
                            w.winner = player_win
                            break

                for w in tournament.lose_grids:
                    if not w.winnerId:
                        if player_win in w.games:
                            w.winner = player_win
                            break

                # Бинарное дерево для хранения сетки
                binary_tree_win = DBSession.query(WinGrid).filter_by(tournament=tournament).all()[::-1]
                binary_tree_lose = sorted(DBSession.query(LoseGrid).filter(LoseGrid.tour % 2 == 1,
                                                                           LoseGrid.tournament == tournament).all(),
                                          key=lambda x: x.tour, reverse=True)
                binary_tree_mix = sorted(DBSession.query(LoseGrid).filter(LoseGrid.tour % 2 == 0,
                                                                          LoseGrid.tournament == tournament).all(),
                                         key=lambda x: x.tour, reverse=True)
                # Заполнение первого тура нижней сетки
                i = 0
                while (i < len(binary_tree_win)):
                    if (binary_tree_win[i].tour == 1 and binary_tree_win[i].winner):
                        if (len(binary_tree_lose[math.floor((i - 1) / 2)].games) != 2 and len(
                                binary_tree_win[i].games) == 2):
                            loser = binary_tree_win[i].games[1] if (
                            binary_tree_win[i].winner == binary_tree_win[i].games[0]) else binary_tree_win[i].games[
                                0]
                            if (loser not in binary_tree_lose[math.floor((i - 1) / 2)].games):
                                binary_tree_lose[math.floor((i - 1) / 2)].games.append(loser)
                    i += 1
                # Заполнение верхней сетки и помещение проигравших в нижнюю
                i = 0
                while (i < len(binary_tree_win) / 2 - 1):
                    if (not binary_tree_win[i].winner):
                        if (len(binary_tree_win[i].games) != 2):
                            if (binary_tree_win[2 * i + 1].winner and binary_tree_win[2 * i + 1].winner not in
                                binary_tree_win[i].games):
                                binary_tree_win[i].games.append(binary_tree_win[2 * i + 1].winner)
                            if (binary_tree_win[2 * i + 2].winner and binary_tree_win[2 * i + 2].winner not in
                                binary_tree_win[i].games):
                                binary_tree_win[i].games.append(binary_tree_win[2 * i + 2].winner)
                    else:
                        if (len(binary_tree_win[i].games) == 2):
                            loser = binary_tree_win[i].games[1] if (
                            binary_tree_win[i].winner == binary_tree_win[i].games[0]) else binary_tree_win[i].games[
                                0]
                            if (loser not in binary_tree_mix[i].games):
                                binary_tree_mix[i].games.append(loser)
                    i += 1

                # Заполнение нижней сетки
                i = 0
                while (i < len(binary_tree_lose)):
                    if (not binary_tree_lose[i].winner and binary_tree_lose[i].tour == 1 and binary_tree_win[
                                2 * i + 1].winner and len(binary_tree_win[2 * i + 1].games) == 0
                        and len(binary_tree_win[2 * i + 2].games) == 2 and binary_tree_win[2 * i + 2].winner):
                        loser = binary_tree_win[2 * i + 2].games[1] if (
                        binary_tree_win[2 * i + 2].winner == binary_tree_win[2 * i + 2].games[0]) else \
                        binary_tree_win[2 * i + 2].games[0]
                        binary_tree_lose[i].winner = loser
                    if (not binary_tree_mix[i].winner and binary_tree_win[i].winner and len(
                            binary_tree_lose[i].games) == 0 and not binary_tree_lose[i].winner):
                        loser = binary_tree_win[i].games[1] if (
                        binary_tree_win[i].winner == binary_tree_win[i].games[0]) else binary_tree_win[i].games[0]
                        binary_tree_mix[i].winner = loser
                    i += 1
                i = 0
                while (i < len(binary_tree_lose)):
                    if (binary_tree_lose[i].winner and binary_tree_lose[i].winner not in binary_tree_mix[i].games):
                        binary_tree_mix[i].games.append(binary_tree_lose[i].winner)
                    if (binary_tree_mix[i].winner and binary_tree_mix[i].winner not in binary_tree_lose[
                        math.floor((i - 1) / 2)].games):
                        binary_tree_lose[math.floor((i - 1) / 2)].games.append(binary_tree_mix[i].winner)
                    i += 1
                return HTTPFound(location="/tournament/" + str(event.id))

        if request.matched_route.name == 'api_tournament_detail':
            list = []
            list2 = []

            for tournament in tournaments:
                players = []
                for player in tournament.players:
                    players.append({
                        "id": player.id,
                        "first_name": player.first_name,
                        "middle_name": player.middle_name,
                        "last_name": player.last_name,
                        "age": player.age,
                        "sex": player.sex,
                        "weight": player.weight,
                        "team": player.team,
                        "event_id": player.eventId
                    })

                list2.append({
                    "id": tournament.id,
                    "hand": tournament.hand,
                    "type_id": tournament.typeId,
                    "weight": tournament.weight,
                    "players": players
                })

            for table in list_table:
                list.append({
                    "number": table[0].number,
                    "tournament_id": table[0].tournamentId,
                    "games": table[1]
                })
            return {
                "tables": list,
                "tournaments":list2
            }

        return{
            "event":event,
            "start":start,
            "tournaments":tournaments,
            "list_table":list_table
        }
    else:
        return HTTPNotFound()
