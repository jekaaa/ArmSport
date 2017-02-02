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

        i = 0
        j = 1
        #Количество халявщиков
        dif = number_players_1tour - number_players
        #Количество пар в первом туре
        pare = (number_players - dif)/2
        #Index for players
        l = 0
        #Создание всех туров сетки виннеров и заполнение 1 тура
        while(i<number_players_1tour-1):
            k = 0
            while(k<number_games_in_tour):
                if j == 1:
                    if pare>0:
                        win_grid = WinGrid(tour=j, tournament=tournament)
                        DBSession.add(win_grid)
                        win_grid.games.append(players[l])
                        win_grid.games.append(players[l+1])
                        l+=2
                        pare-=1
                    else:
                        win_grid = WinGrid(tour=j, tournament=tournament,winner=players[l])
                        DBSession.add(win_grid)
                        l+=1
                else:
                    win_grid = WinGrid(tour=j, tournament=tournament)
                    DBSession.add(win_grid)
                k += 1
            i += number_games_in_tour
            number_games_in_tour//=2
            j+=1


        '''j = 0
        k = 0
        while (j < number_games_in_tour):
            if len(players) % 2 == 1:
                if k == len(players) - 1:
                    win_grid = WinGrid(tour=1, tournament=tournament, winner=players[k])
                    DBSession.add(win_grid)
                    break
            win_grid = WinGrid(tour=1, tournament=tournament)
            DBSession.add(win_grid)
            win_grid.games.append(players[k])
            win_grid.games.append(players[k+1])
            j += 1
            k += 2'''

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

        #Бинарное дерево для хранения сетки виннеров
        for tournament in tournaments:
            binary_tree = []
            all_tours = DBSession.query(WinGrid).filter_by(tournament=tournament).all()
            i = len(all_tours)-1
            while(i>=0):
                binary_tree.append(all_tours[i])
                i-=1
            i=0
            while(i<len(binary_tree)/2-1):
                if(not binary_tree[i].winner):
                    if(not len(binary_tree[i].games)==2):
                        if (binary_tree[2*i+1].winner and binary_tree[2*i+1].winner not in binary_tree[i].games):
                            binary_tree[i].games.append(binary_tree[2*i+1].winner)
                        if (binary_tree[2*i+2].winner and binary_tree[2*i+2].winner not in binary_tree[i].games):
                            binary_tree[i].games.append(binary_tree[2 * i + 2].winner)
                i+=1

        #Вывод турниров на столы
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


            #dict_table[table.number] = table.tournament.win_grids
            games = []
            for w in table.tournament.win_grids:
                full_list = []
                if w.winnerId is None:
                    for l in w.games:
                        full_name = l.middle_name + " " + l.first_name
                        full_list.append(full_name)
                    games.append(full_list)
                    dict_table[table] = games
                else:
                    dict_table[table]=[]

            list_table = gold_sort_tables(dict_table)

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
                    if w.winnerId is None:
                        if player_win in w.games:
                            w.winner = player_win
                            break

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
'''
@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    try:
        query = request.dbsession.query(MyModel)
        one = query.filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'armsport'}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_armsport_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
'''