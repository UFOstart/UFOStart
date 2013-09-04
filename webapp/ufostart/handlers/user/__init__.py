from pyramid.decorator import reify

from . import index
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.models.procs import RefreshProfileProc, GetProfileProc, GetFriendsProc, GetFriendsCompaniesProc


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
    def is_my_profile(self):
        return self.user.slug == self.__name__

    @reify
    def profile(self):
        if self.user.slug == self.__name__:
            RefreshProfileProc(self.request, {'slug': self.__name__})
            return self.user
        else:
            return GetProfileProc(self.request, {'slug': self.__name__})


    @reify
    def contacts(self):
        result = GetFriendsProc(self.request, {'slug': self.__name__})
        return result.Users
    @reify
    def companies(self):
        result = GetFriendsCompaniesProc(self.request, {'slug': self.__name__})
        return result

def includeme(config):
    config.add_view(index.user      , context = UserProfileContext, renderer = "ufostart:templates/user/home.html")
