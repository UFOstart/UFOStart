from . import index
import urllib
from pyramid.decorator import reify
from pyramid.security import Authenticated, Allow, Deny, Everyone
from pyramid.traversal import quote_path_segment
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.models.procs import RefreshProfileProc, GetProfileProc, GetTopTags, FindPublicNeeds




class ProtoProfileContext(BaseContextMixin):
    displayType = 'User Profile'
    @reify
    def displayName(self):
        return self.profile.name

    @property
    def site_title(self):
        return [self.displayName, self.request.globals.project_name]



class UserProfileContext(ProtoProfileContext):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    @reify
    def profile(self):
        if self.user.slug == self.__name__:
            RefreshProfileProc(self.request, {'slug': self.__name__})
            return self.user
        else:
            return GetProfileProc(self.request, {'slug': self.__name__})




def includeme(config):
    config.add_view(index.user      , context = UserProfileContext, renderer = "ufostart:templates/user/home.html")
