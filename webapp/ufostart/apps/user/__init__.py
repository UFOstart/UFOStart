from . import index
import urllib
from pyramid.decorator import reify
from pyramid.security import Authenticated, Allow, Deny, Everyone
from pyramid.traversal import quote_path_segment
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.apps.models.procs import RefreshProfileProc, GetProfileProc, GetTopTags, FindPublicNeeds




class ProtoProfileContext(BaseContextMixin):
    displayType = 'User Profile'
    @reify
    def displayName(self):
        return self.profile.name

    @property
    def site_title(self):
        return [self.displayName, self.request.globals.project_name]



class UserHomeContext(ProtoProfileContext):
    __acl__ = [(Allow, Authenticated, 'view'), (Deny, Everyone, 'view')]
    __auth_template__ = "ufostart:templates/auth/login.html"
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.user_token = parent.user.token
    @reify
    def profile(self):
        return RefreshProfileProc(self.__parent__.request, {'token': self.user_token})


class UserProfileContext(ProtoProfileContext):
    def __init__(self, parent, name, profile):
        self.__parent__ = parent
        self.__name__ = name
        self.profile = profile


class UserStubContext(BaseContextMixin):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
    def __getitem__(self, item):
        return UserProfileContext(self, item, GetProfileProc(self.request, {'token': item}))



class BrowseTagContext(BaseContextMixin):
    @property
    def tags(self):
        return self.__parent__.tags

    @property
    def site_title(self):
        return [self.tag, 'Browse', self.request.globals.project_name]

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.tag = urllib.unquote(name)
    def browse_url(self, tag): return self.__parent__.browse_url(tag)
    @reify
    def tasks(self):
        return FindPublicNeeds(self.request, {'Search': {'tags': [{'url':self.tag}]}})


class BrowseContext(BaseContextMixin):

    @property
    def site_title(self):
        return ['Browse', self.request.globals.project_name]

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.tags = GetTopTags(self.request)
        self.tag = self.tags[0].name


    def browse_url(self, tag):
        return self.request.resource_url(self, quote_path_segment(tag))

    def __getitem__(self, item):
        return BrowseTagContext(self, item)

    @reify
    def tasks(self):
        return FindPublicNeeds(self.request, {'Search': {'tags': [{'url':self.tag}]}})



def includeme(config):
    config.add_view(index.home      , context = UserHomeContext, renderer = "ufostart:templates/user/home.html",permission='view')
    config.add_view(index.user      , context = UserProfileContext, renderer = "ufostart:templates/user/home.html")
    config.add_view(index.browse    , context = BrowseContext, renderer = "ufostart:templates/user/browse.html")
    config.add_view(index.browse    , context = BrowseTagContext, renderer = "ufostart:templates/user/browse.html")


