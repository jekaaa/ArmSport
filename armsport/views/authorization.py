from pyramid.response import Response
from pyramid.view import view_config,forbidden_view_config

from pyramid.httpexceptions import (
HTTPFound,
HTTPNotFound,
)

from pyramid.security import (
remember,
forget,
)

from sqlalchemy.exc import DBAPIError

from ..models import *

@view_config(route_name='login',renderer='templates/login.jinja2')
@forbidden_view_config(renderer='templates/login.jinja2')
@view_config(route_name='apiLogin', renderer='myjson')
def login_view(request):
    if request.matched_route.name == 'apiLogin':
        if 'login' in request.params:
            login = request.params['login']
            model = DBSession.query(User).filter_by(login=login).first()
            if model:
                if 'password' in request.params:
                    password = request.params['password']
                    model = DBSession.query(User).filter_by(login=login,password=password).first()
                    if model:
                        return {
                            'login':True,
                            'password':True
                        }
                    else:
                        return {
                            'login':True,
                            'password':False
                        }
                else:
                    return {
                        'login':True
                    }
            else:
                return{
                    'login':False
                }
        else:
            return {
                'login':False
            }

    if 'submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = DBSession.query(User).filter_by(login = login).first()
        if user:
            if user.password == password:
                headers = remember(request, login)
                return HTTPFound(location = '/all_tournaments', headers = headers)
        return {'message': "Неверный логин или пароль"}
        #return HTTPNotFound()
    if 'reg' in request.params:
        return HTTPFound(location='/registration')
    return {}


@view_config(route_name='logout')
def logout_view(request):
	headers = forget(request)
	return HTTPFound(location = '/',headers = headers)

@view_config(route_name='reg',renderer='templates/registration.jinja2')
def reg_view(request):
    if 'reg' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = DBSession.query(User).filter_by(login=login).first()
        if (not user  and login != " " and password != " " and login != "" and password != ""):
            model = User(login=login,password=password)
            DBSession.add(model)
            headers = remember(request, login)
            return HTTPFound(location = '/all_tournaments',headers=headers)
        return {'message':"Такой логин уже существует"}
    return{}