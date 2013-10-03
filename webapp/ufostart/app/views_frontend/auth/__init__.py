from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import Everyone, Allow, Authenticated, NO_PERMISSION_REQUIRED

from . import social, imp, signup
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.app.models.auth import setUserF, getUser
from ufostart.app.views_frontend.social import angellist, SocialLoginFailed, SocialLoginSuccessful

def t_path(p): return "ufostart:templates_frontend/{}".format(p)

class SocialContext(BaseContextMixin):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'proceed')]

    user = reify(getUser)
    setUser = setUserF

    @property
    def site_title(self):
        return [self.__name__.title(), self.request.globals.project_name]


    def __getitem__(self, item):
        if item in self.settings.networks:
            settings = self.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            raise KeyError()

class UserNameContext(BaseContextMixin):
    has_username = True

    def __getitem__(self, item):
        if item in self.settings.networks:
            settings = self.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            raise KeyError()

    @property
    def site_title(self):
        return self.__parent__.site_title

class SignupContext(BaseContextMixin):
    has_username = False
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'proceed')]

    @property
    def site_title(self):
        return ['Pick a username', self.request.globals.project_name]

    def __getitem__(self, item):
        if item in ['isavailable', 'getstarted']: raise KeyError()
        return UserNameContext(self, item)


def includeme(config):


    config.add_view(signup.UserNameHandler                   , context = SignupContext, renderer=t_path("auth/username.html"), permission = NO_PERMISSION_REQUIRED)
    config.add_view(signup.UserNameHandler                   , context = UserNameContext, renderer=t_path("auth/username.html"), permission = NO_PERMISSION_REQUIRED)
    config.add_view(signup.isavailable, name = "isavailable" , context = SignupContext, renderer = "json", permission = NO_PERMISSION_REQUIRED)


    config.add_view(signup.login_success                     , containment = UserNameContext, context = SocialLoginSuccessful, permission = NO_PERMISSION_REQUIRED)
    config.add_view(signup.login_failure                     , containment = UserNameContext, context = SocialLoginFailed, permission = NO_PERMISSION_REQUIRED)
    config.add_view(signup.UserRoleHandler, name="getstarted", context = SignupContext, renderer = t_path("auth/roleselect.html"), permission = 'proceed')


    config.add_view(social.login                             , context = SocialContext, permission='proceed')
    config.add_view(social.login_success                     , context = SocialLoginSuccessful, permission = NO_PERMISSION_REQUIRED)
    config.add_view(social.login_failure                     , context = SocialLoginFailed, permission = NO_PERMISSION_REQUIRED)

    config.add_view(social.auth_required_view                , context = social.RequiresLoginException, permission = NO_PERMISSION_REQUIRED)
    config.add_view(social.auth_required_view                , context = HTTPForbidden, permission = NO_PERMISSION_REQUIRED)

    config.add_view(imp.company_import_start                 , context = angellist.SocialResource, permission='import')
    config.add_view(imp.company_import                       , context = angellist.SocialResource, name = 'import'   , permission='import')
    config.add_view(imp.company_import_list                  , context = angellist.SocialResource, name = 'list'     , renderer = t_path("company/import/list.html"), permission='import')
    config.add_view(imp.company_import_confirm               , context = angellist.SocialResource, name = 'confirm'  , permission='import')
