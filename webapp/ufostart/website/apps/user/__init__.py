from . import index
from pyramid.decorator import reify
from pyramid.security import Authenticated, Allow, Deny, Everyone
from ufostart.website.apps.models.procs import RefreshProfileProc, GetProfileProc


class UserHomeContext(object):
    __acl__ = [(Allow, Authenticated, 'view'), (Deny, Everyone, 'view')]
    __auth_template__ = "ufostart:website/templates/auth/login.html"
    def __init__(self, parent, name, token):
        self.__parent__ = parent
        self.__name__ = name
        self.user_token = token
    @reify
    def user(self):
        return RefreshProfileProc(self.__parent__.request, {'token': self.user_token})

class UserProfileContext(object):
    def __init__(self, parent, name, profile):
        self.__parent__ = parent
        self.__name__ = name
        self.profile = profile

class UserProtoContext(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
    def __getitem__(self, item):
        request = self.__parent__.request
        return UserProfileContext(self, item, GetProfileProc(request, {'token': item}))

def includeme(config):
    config.add_view(index.home      , context = UserHomeContext, renderer = "ufostart:website/templates/user/home.html",permission='view')
    config.add_view(index.user      , context = UserProfileContext, renderer = "ufostart:website/templates/user/home.html")
