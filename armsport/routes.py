from pyramid.renderers import JSON
def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('myjson', JSON(indent=4, ensure_ascii=False))

    config.add_route('new_tournament', '/new_tournament')
    config.add_route('api_new_tournament','/api/v1/new')
    config.add_route('my_tournaments','/my_tournaments')
    config.add_route('login','/')
    config.add_route('logout', '/logout')
    config.add_route('reg','/registration')
    config.add_route('all_tournaments','/all_tournaments')
    config.add_route('tournament_detail','/tournament/{name}')
    config.add_route('api_all_tournaments','/api/v1/all_tournaments')
    config.add_route('api_tournament_detail', '/api/v1/tournament/{name}')
    config.add_route('apiLogin','/api/v1/auth')
    config.add_route('apiFavorites','/api/v1/favorites')
    config.add_route('api_my_tournaments','/api/v1/my')
