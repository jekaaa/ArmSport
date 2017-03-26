from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import *
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy('sosecret', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,root_factory='.security.Group')

    #config.include('pyramid_sacrud')
    #settings = config.registry.settings
    #settings['pyramid_sacrud.models'] = (('Group1', [User]),
    #                                     ('Group2', [Event]))

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_jinja2')
    config.include('.routes')
    #config.include('ps_alchemy')

    config.scan()
    return config.make_wsgi_app()