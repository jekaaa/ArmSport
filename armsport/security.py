from pyramid.security import (
Allow,
Authenticated
)

class Group(object):
    def __init__(self, request):
       self.__acl__ = [
    (Allow, Authenticated, 'view')]