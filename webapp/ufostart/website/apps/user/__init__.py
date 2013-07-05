from . import index
from pyramid.decorator import reify
from pyramid.security import Authenticated, Allow, Deny, Everyone
from ufostart.website.apps.models.procs import RefreshProfileProc, GetProfileProc, GetTopTags, FindPublicNeeds


class ProtoProfileContext(object):
    displayType = 'User Profile'
    @reify
    def displayName(self):
        return self.profile.name

    @property
    def site_title(self):
        return [self.displayName, self.request.globals.project_name]

    @property
    def request(self):
        return self.__parent__.request

class UserHomeContext(ProtoProfileContext):
    __acl__ = [(Allow, Authenticated, 'view'), (Deny, Everyone, 'view')]
    __auth_template__ = "ufostart:website/templates/auth/login.html"
    def __init__(self, parent, name, token):
        self.__parent__ = parent
        self.__name__ = name
        self.user_token = token
    @reify
    def profile(self):
        return RefreshProfileProc(self.__parent__.request, {'token': self.user_token})


class UserProfileContext(ProtoProfileContext):
    def __init__(self, parent, name, profile):
        self.__parent__ = parent
        self.__name__ = name
        self.profile = profile


class UserStubContext(object):
    @property
    def request(self):
        return self.__parent__.request

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
    def __getitem__(self, item):
        return UserProfileContext(self, item, GetProfileProc(self.request, {'token': item}))



class BrowseTagContext(object):
    @property
    def request(self):
        return self.__parent__.request
    @property
    def tags(self):
        return self.__parent__.tags

    @property
    def site_title(self):
        return [self.__name__, 'Browse', self.request.globals.project_name]

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.tasks = FindPublicNeeds(self.request, {'Search': {'tags': [name]}})
        self.tag = name
    def browse_url(self, tag):
        return self.request.resource_url(self.__parent__, tag)

class BrowseContext(object):
    @property
    def request(self):
        return self.__parent__.request
    @property
    def site_title(self):
        return ['Browse', self.request.globals.project_name]

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.tags = GetTopTags(self.request)
        self.tag = self.tags[0].name


    def browse_url(self, tag):
        return self.request.resource_url(self, tag)

    def __getitem__(self, item):
        return BrowseTagContext(self, item)

    @reify
    def tasks(self):
        return FindPublicNeeds(self.request, {'Search': {'tags': [self.tag]}})



def includeme(config):
    config.add_view(index.home      , context = UserHomeContext, renderer = "ufostart:website/templates/user/home.html",permission='view')
    config.add_view(index.user      , context = UserProfileContext, renderer = "ufostart:website/templates/user/home.html")
    config.add_view(index.browse    , context = BrowseContext, renderer = "ufostart:website/templates/user/browse.html")
    config.add_view(index.browse    , context = BrowseTagContext, renderer = "ufostart:website/templates/user/browse.html")


