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
'''def sort_result_dict(dict):
    list = []
    ex = None
    for t in dict.items():
        try:
            s = t[0].split(' ')[1]
            s = s.split('к')[0]
            if(int(s)):
                list.append(t)
        except:
            ex=t
    list.sort(key=lambda x: int(x[0].split(' ')[1].split('к')[0]))
    if ex:
        list.append(ex)
'''
def tournament_grid(dict_table,table,split_winner):
    first_name = split_winner[2]
    middle_name = split_winner[1]
    player_win = dict_table[table][0][1].games[0] if first_name == dict_table[table][0][1].games[0].first_name and middle_name == dict_table[table][0][1].games[0].middle_name else dict_table[table][0][1].games[1]
    if not dict_table[table][0][1].winner:
        dict_table[table][0][1].winner = player_win

    list_win_grid = DBSession.query(WinGrid).filter_by(tournament=table.tournament).all()
    number_players = len(table.tournament.players)
    number_games = math.ceil(number_players/2)

    l = 0
    index_free = 0
    while (number_games > 0):
        k = 0
        index_free += number_games
        if list_win_grid[index_free-1].winner and len(list_win_grid[index_free-1].games) == 0 and \
                        list_win_grid[index_free-1].winner not in list_win_grid[index_free].games:
            list_win_grid[index_free].games.append(list_win_grid[index_free-1].winner)
        while (k < number_games):
            #if k == number_games-1 and list_win_grid[l].winner and len(list_win_grid[l].games) == 0 and list_win_grid[l].winner not in list_win_grid[number_games-k+l].games:
            #    list_win_grid[number_games - k + l].games.append(list_win_grid[l].winner)
            if list_win_grid[l].winner:
                g = 0
                next_tour_number_games = 0 if number_games == 1 else math.ceil(number_games / 2)
                while(g < next_tour_number_games):
                    if list_win_grid[l].winner in list_win_grid[number_games - k + l + g].games:
                        break
                    if len(list_win_grid[number_games - k + l + g].games) < 2:
                        if g == next_tour_number_games - 1 and math.ceil(number_players / 2) % 2 == 1:
                            list_win_grid[number_games - k + l + g].winner = list_win_grid[l].winner
                        else:
                            list_win_grid[number_games - k + l + g].games.append(list_win_grid[l].winner)
                        break
                    g += 1
            l += 1
            k += 1

        number_players = math.ceil(number_players / 2)
        number_games = 0 if number_games == 1 else math.ceil(number_games / 2)

def tournament_grid_olympic(dict_table,table,event,split_winner):
    first_name = split_winner[2]
    middle_name = split_winner[1]
    player_win = DBSession.query(Player).filter_by(event=event, first_name=first_name, middle_name=middle_name).first()
    if not dict_table[table][0][1].winner:
        dict_table[table][0][1].winner = player_win
    # Бинарное дерево для хранения сетки
    binary_tree_win = DBSession.query(WinGrid).filter_by(tournament=table.tournament).all()[::-1]
    binary_tree_lose = sorted(DBSession.query(LoseGrid).filter(LoseGrid.tour % 2 == 1,
                                                               LoseGrid.tournament == table.tournament).all(),
                              key=lambda x: x.tour, reverse=True)
    binary_tree_mix = sorted(DBSession.query(LoseGrid).filter(LoseGrid.tour % 2 == 0,
                                                              LoseGrid.tournament == table.tournament).all(),
                             key=lambda x: x.tour, reverse=True)
    final = DBSession.query(Final).filter_by(tournament=table.tournament).first()

    # Заполнение финала
    if (binary_tree_win[0].winner and binary_tree_mix[0].winner and len(final.games) != 2):
        final.games.append(binary_tree_win[0].winner)
        final.games.append(binary_tree_mix[0].winner)

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

# Формирование словаря с результатами всех пройденных матчей
def result(tournaments,dict_result):
    for tournament in tournaments:
        games = []
        list_one_tour = ["1A"]
        for w in tournament.win_grids:
            if w.tour == 1:
                list_one_tour.append(w)
        games.append(list_one_tour)
        i = 2
        j = 1
        tours = math.log2(len(DBSession.query(WinGrid).filter_by(tournament=tournament).all()) + 1)

        while (i <= tours):
            list_win_tour = [str(i) + "A"]
            for w in tournament.win_grids:
                if w.tour == i:
                    list_win_tour.append(w)
            games.append(list_win_tour)

            list_lose_tour = [str(j) + "B"]
            for w in tournament.lose_grids:
                if w.tour == j:
                    list_lose_tour.append(w)
            games.append(list_lose_tour)

            list_lose_tour2 = [str(j + 1) + "B"]
            for w in tournament.lose_grids:
                if w.tour == j + 1:
                    list_lose_tour2.append(w)
            games.append(list_lose_tour2)

            j += 2
            i += 1

        list_final = ["Финал"]
        if len(tournament.final[0].games) > 0:
            list_final.append(tournament.final[0])
        games.append(list_final)

        hand = "кг (правая)" if tournament.hand else "кг (левая)"
        sex = "М " if tournament.typeId == 2 else "Ж "
        dict_result[sex + tournament.weight + hand] = games

        lenght = len(dict_result.items())/2
    return dict_result

# Формирование игр на столе
def games_on_table(table,games):
    for w in table.tournament.win_grids:
        if not w.winner and len(w.games) > 0 and w.tour == 1:
            # games.append([(str(w.tour)+"A",l.middle_name + " " + l.first_name) for l in w.games])
            games.append((str(w.tour) + "A", w))
    i = 2
    j = 1

    tours = math.ceil(math.log2(len(DBSession.query(WinGrid).filter_by(tournament=table.tournament).all()) + 1))

    while (i <= tours):
        for w in table.tournament.win_grids:
            if not w.winnerId and len(w.games) > 0 and w.tour == i:
                # games.append([(str(w.tour)+"A",l.middle_name + " " + l.first_name) for l in w.games])
                games.append((str(w.tour) + "A", w))

        for w in table.tournament.lose_grids:
            if not w.winnerId and len(w.games) > 0 and w.tour == j:
                # games.append([(str(w.tour)+"B",l.middle_name + " " + l.first_name) for l in w.games])
                games.append((str(w.tour) + "B", w))

        for w in table.tournament.lose_grids:
            if not w.winnerId and len(w.games) > 0 and w.tour == j + 1:
                # games.append([(str(w.tour)+"B",l.middle_name + " " + l.first_name) for l in w.games])
                games.append((str(w.tour) + "B", w))
        j += 2
        i += 1

    if not table.tournament.final[0].winnerId and len(table.tournament.final[0].games) > 0:
        # games.append([("Финал",l.middle_name + " " + l.first_name) for l in table.tournament.final[0].games])
        games.append(("Финал", table.tournament.final[0]))
    return games

# Перевод даты в нормальную)
def convert_time(date):
    if date != "":
        d = date.split('-')
        date = d[2] + "." + d[1] + "." + d[0]
    return date

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

def first_tour(tournaments):
    for tournament in tournaments:
        # Все участники
        players = tournament.players
        # Количество участников
        number_players = len(players)
        # Количество игр в 1 туре
        number_games = math.ceil(number_players/2)

        if tournament.hand:
            players.sort(key=lambda x: int(x.right_hand))
        else:
            players.sort(key=lambda x: int(x.left_hand))

        # Туры в сетке виннеров
        tour_win = 1
        # Туры в сетке лузеров
        tour_lose = 1
        # Индексы для игроков
        l = 0
        # Создание всех туров сетки и заполнение 1 тура
        while (number_games > 0):
            k = 0
            while (k < number_games):
                if tour_win == 1:
                    if l+1 <= number_players-1:
                        win_grid = WinGrid(tour=tour_win, tournament=tournament, gap=False, first_fouls=0,
                                           second_fouls=0)
                        DBSession.add(win_grid)
                        win_grid.games.append(players[l])
                        win_grid.games.append(players[l + 1])
                        l += 2
                    else:
                        win_grid = WinGrid(tour=tour_win, tournament=tournament, winner=players[l], gap=False,
                                           first_fouls=0, second_fouls=0)
                        DBSession.add(win_grid)
                        l += 1
                else:
                    win_grid = WinGrid(tour=tour_win, tournament=tournament, gap=False, first_fouls=0,
                                       second_fouls=0)
                    lose_grid1 = LoseGrid(tour=tour_lose, tournament=tournament, gap=False, first_fouls=0,
                                          second_fouls=0)
                    lose_grid2 = LoseGrid(tour=tour_lose + 1, tournament=tournament, gap=False, first_fouls=0,
                                          second_fouls=0)
                    DBSession.add_all([win_grid, lose_grid1, lose_grid2])
                k += 1

            number_games = 0 if number_games == 1 else math.ceil(number_games/2)

            if tour_win != 1:
                tour_lose += 2
            tour_win += 1
        # Создание финала
        final = Final(tournament=tournament, gap=False, first_fouls=0, second_fouls=0)
        DBSession.add(final)

def first_tour_olympic(tournaments):
    for tournament in tournaments:
        #Все участники
        players = tournament.players
        #Количество участников
        number_players = len(players)
        #Количество участников в 1 туре
        number_players_1tour = 0

        if tournament.hand:
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
                        win_grid = WinGrid(tour=tour_win, tournament=tournament,gap=False,first_fouls=0,second_fouls=0)
                        DBSession.add(win_grid)
                        win_grid.games.append(players[l])
                        win_grid.games.append(players[l+1])
                        l+=2
                        pare-=1
                    else:
                        win_grid = WinGrid(tour=tour_win, tournament=tournament,winner=players[l],gap=False,first_fouls=0,second_fouls=0)
                        DBSession.add(win_grid)
                        l+=1
                else:
                    win_grid = WinGrid(tour=tour_win, tournament=tournament,gap=False,first_fouls=0,second_fouls=0)
                    lose_grid1 = LoseGrid(tour=tour_lose, tournament=tournament,gap=False,first_fouls=0,second_fouls=0)
                    lose_grid2 = LoseGrid(tour=tour_lose+1, tournament=tournament,gap=False,first_fouls=0,second_fouls=0)
                    DBSession.add_all([win_grid,lose_grid1,lose_grid2])
                k += 1

            number_games_in_tour//=2
            if tour_win !=1:
                tour_lose += 2
            tour_win+=1
        # Создание финала
        final = Final(tournament=tournament,gap=False,first_fouls=0,second_fouls=0)
        DBSession.add(final)

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
            date = convert_time(request.params['date'])
        else:
            date = ""

        if 'date2' in request.params:
            date2 = convert_time(request.params['date2'])
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
                    t = Tournament(hand=0, event=event, type=type, weight=weight.strip())
                    t2 = Tournament(hand=1, event=event, type=type, weight=weight.strip())
                    DBSession.add_all([t,t2])

            weight_woman = weight_woman.split(',')
            type = DBSession.query(Type).filter_by(id=1).first()
            for weight in weight_woman:
                if weight != "":
                    t = Tournament(hand=0, event=event, type=type, weight=weight.strip())
                    t2 = Tournament(hand=1, event=event, type=type, weight=weight.strip())
                    DBSession.add_all([t,t2])
        else:
            if weight_man:
                type = DBSession.query(Type).filter_by(id=2).first()
                weight_man = weight_man.split(',')
                for weight in weight_man:
                    if weight != "":
                        t = Tournament(hand=0,event=event,type=type,weight=weight.strip())
                        t2 = Tournament(hand=1, event=event, type=type, weight=weight.strip())
                        DBSession.add_all([t,t2])

            if weight_woman:
                type = DBSession.query(Type).filter_by(id=1).first()
                weight_woman = weight_woman.split(',')
                for weight in weight_woman:
                    if weight != "":
                        t = Tournament(hand=0, event=event, type=type, weight=weight.strip())
                        t2 = Tournament(hand=1, event=event, type=type, weight=weight.strip())
                        DBSession.add_all([t,t2])

        return HTTPFound(location='/my_tournaments')
    return {}

@view_config(route_name='tournament_detail', renderer='templates/tournamentDetail.jinja2')
@view_config(route_name='api_tournament_detail', renderer='myjson')
def td_view(request):
    id = request.matchdict['name']
    event = DBSession.query(Event).filter_by(id=id).first()
    if event:
        # Количество столов
        tables_number = event.numberTable

        # Получение всех турниров мероприятия
        tournaments = event.tournaments

        # Проверка на начало турниров
        start = False
        # Проверка на наличие прав редактирования
        user = DBSession.query(User).filter_by(login=request.authenticated_userid).first()
        userEvent = DBSession.query(User).filter_by(id=event.userId).first()
        root = True if user == userEvent else False

        # Словари для распределения участников по весовым категориям
        # Заполнение данными словарей с участниками турнира
        for tournament in tournaments:
            if tournament.win_grids:
                start = True

        dict_tournaments_woman = {tournament.weight:tournament.players for tournament in tournaments if tournament.hand and tournament.typeId == 1}
        dict_tournaments_man = {tournament.weight:tournament.players for tournament in tournaments if tournament.hand and tournament.typeId == 2}

        # Упорядочивание по весовым категориям
        list_tournaments_man = gold_sort_dict(dict_tournaments_man)
        list_tournaments_woman = gold_sort_dict(dict_tournaments_woman)

        # Не стартовавшее мероприятие
        if not start:
            # Старт мероприятия
            if root and 'start' in request.params:
                for w in list_tournaments_man:
                    if len(w[1])<3:
                        return {"event": event,
                                "message2":"В каждой весовой категории должно быть минимум 3 участника",
                                "dict_tournaments_man": list_tournaments_man,
                                "dict_tournaments_woman": list_tournaments_woman}
                for w in list_tournaments_woman:
                    if len(w[1]) < 3:
                        return {"event": event,
                                "message2": "В каждой весовой категории должно быть минимум 3 участника",
                                "dict_tournaments_man": list_tournaments_man,
                                "dict_tournaments_woman": list_tournaments_woman}
                first_tour(tournaments)
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

            # Добавление участника
            if root and 'settings' in request.params:
                # Возраст
                if 'age' in request.params:
                    age = convert_time(request.params['age'])
                else:
                    age = ""
                # ФИО
                first_name = request.params['first_name'] if 'first_name' in request.params else ""
                middle_name = request.params['middle_name'] if 'middle_name' in request.params else ""
                last_name = request.params['last_name'] if 'last_name' in request.params else ""
                # Пол
                sex = request.params['sex']
                sex = 0 if sex == "Женщина" else 1
                # Вес
                if 'weight' in request.params:
                    weight = request.params['weight']
                    if ',' in weight:
                        weight = weight.replace(',','.')
                    weight = float(weight)
                else:
                    return {"event":event,
                            "dict_tournaments_man": list_tournaments_man,
                            "dict_tournaments_woman": list_tournaments_woman,
                            "message":"Вес неверен"}
                # Команда
                team = request.params['team'] if 'team' in request.params else ""
                random_left = random.randint(1,1000)
                random_right = random.randint(1,1000)

                type_id = 2 if sex else 1
                ts_left = DBSession.query(Tournament).filter_by(typeId=type_id, hand=0, event=event).all()
                ts_right = DBSession.query(Tournament).filter_by(typeId=type_id, hand=1, event=event).all()
                # Все турниры для участника
                player_tournaments = tournaments_for_player(ts_left, ts_right, weight)

                if not player_tournaments:
                    return {"event":event,
                            "dict_tournaments_man": list_tournaments_man,
                            "dict_tournaments_woman": list_tournaments_woman,
                            "message":"Нет турнира для этого участника"}
                # Добавление нового участника
                player = Player(first_name=first_name,middle_name=middle_name,last_name=last_name,left_hand=random_left,
                                     right_hand=random_right,age=age,sex=sex,weight=weight,team=team,event=event)
                DBSession.add(player)
                # Добавление во все подходящие участнику турниры
                for tournament in player_tournaments:
                    tournament.players.append(player)
                return HTTPFound(location="/tournament/"+str(event.id))

            return {"event":event,
                    "dict_tournaments_man":list_tournaments_man,
                    "dict_tournaments_woman":list_tournaments_woman}

        #Стартовавшее мероприятие
        dict_table = {}
        tables = event.tables

        # Создание словаря с результатами матчей
        dict_result = result(tournaments,{})

        # Создание столов
        if not tables:
            i = 0
            while (i < tables_number):
                t = Table(number=i + 1, event=event, tournament=tournaments[0])
                DBSession.add(t)
                i += 1

        # Вывод турниров на столы
        for table in tables:
            # Определение турнира на стол
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

            # Формирование словаря со столами и парами на каждом столе
            dict_table[table] = games_on_table(table,[])

            # Опредение разрыва или фолов в матче
            if str(table.number) + "f" in request.params:
                dict_table[table][0][1].gap = True if "gap" in request.params else False
                if "first_foul_1" in request.params and "second_foul_1" in request.params:
                    dict_table[table][0][1].first_fouls = 2
                elif "first_foul_1" in request.params or "second_foul_1" in request.params:
                    dict_table[table][0][1].first_fouls = 1
                else:
                    dict_table[table][0][1].first_fouls = 0
                if "first_foul_2" in request.params and "second_foul_2" in request.params:
                    dict_table[table][0][1].second_fouls = 2
                elif "first_foul_2" in request.params or "second_foul_2" in request.params:
                    dict_table[table][0][1].second_fouls = 1
                else:
                    dict_table[table][0][1].second_fouls = 0

        #Сортировка словаря со столами и формирование списка со столами, разделенными на 2 части
        list_table = gold_sort_tables(dict_table)
        list_even = [el for el in list_table if el[0].number%2==0]
        list_not_even = [el for el in list_table if el[0].number%2==1]
        list_table = []
        list_table.append(list_not_even)
        list_table.append(list_even)

        # Определение победителя в каком-либо матче и построение сетки
        if root:
            for table in tables:
                if str(table.number) + "c" in request.params:
                    winner = request.params['winner'] if 'winner' in request.params else ""
                    split_winner = winner.split(' ')
                    if winner:
                        tournament_grid(dict_table,table,split_winner)
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
            "list_table":list_table,
            "dict_result":dict_result,
            "root":root
        }
    else:
        return HTTPNotFound()
