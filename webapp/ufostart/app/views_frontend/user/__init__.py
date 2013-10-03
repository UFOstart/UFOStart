from pyramid.decorator import reify

from . import index
from pyramid.security import Everyone, Allow, NO_PERMISSION_REQUIRED, Authenticated
from ufostart.handlers.social import SocialLoginFailed, SocialLoginSuccessful
from ufostart.app.views_frontend import t_path
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
    config.add_view(index.login_success                     , containment=UserProfileContext, context = SocialLoginSuccessful, permission = NO_PERMISSION_REQUIRED)
    config.add_view(index.login_failure                     , containment=UserProfileContext, context = SocialLoginFailed, permission = NO_PERMISSION_REQUIRED)

