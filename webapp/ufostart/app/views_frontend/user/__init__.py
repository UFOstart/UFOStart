from pyramid.decorator import reify
from pyramid.security import Allow, NO_PERMISSION_REQUIRED, Authenticated

from . import index
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.app.views_frontend import social
from ufostart.app.models.procs import RefreshProfileProc, GetProfileProc, GetFriendsProc, GetFriendsCompaniesProc

def t_path(p): return "ufostart:templates_frontend/{}".format(p)

class ProtoProfileContext(BaseContextMixin):
    displayType = 'User Profile'
    @reify
    def displayName(self):
        return self.profile.name

    @property
    def site_title(self):
        return [self.displayName, self.request.globals.project_name]


class UserProfileContext(ProtoProfileContext):
    __acl__ = [(Allow, Authenticated, 'view')]
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    @reify
    def is_my_profile(self):
        return self.user.slug == self.__name__
    @reify
    def possessive_name(self):
        return 'Your' if self.is_my_profile else u"{}'s".format(self.profile.name)

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

    def __getitem__(self, item):
        if item in self.settings.networks:
            settings = self.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            raise KeyError()


def includeme(config):
    config.add_view(index.user                              , context = UserProfileContext, renderer = t_path("user/home.html"), permission = NO_PERMISSION_REQUIRED)
    config.add_view(index.login_success                     , containment=UserProfileContext, context = social.SocialLoginSuccessful, permission = NO_PERMISSION_REQUIRED)
    config.add_view(index.login_failure                     , containment=UserProfileContext, context = social.SocialLoginFailed, permission = NO_PERMISSION_REQUIRED)

