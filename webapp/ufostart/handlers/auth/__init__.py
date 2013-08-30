from . import social, imp
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import Everyone, Allow, Authenticated, NO_PERMISSION_REQUIRED
from ufostart.models.auth import setUserF, getUser
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.handlers.social import angellist, SocialLoginFailed, SocialLoginSuccessful


class SocialContext(BaseContextMixin):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'proceed')]
    __auth_template__ = "ufostart:templates/auth/login.html"

    user = reify(getUser)
    setUser = setUserF

    @property
    def site_title(self):
        return [self.__name__.title(), self.request.globals.project_name]


    def __getitem__(self, item):
        if item in self.__parent__.settings.networks:
            settings = self.__parent__.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            raise KeyError()



class SignupContext(BaseContextMixin):
    pass


def includeme(config):

    config.add_view(signup.index        , context = SignupContext, NO_PERMISSION_REQUIRED)


    config.add_view(social.login        , context = SocialContext, permission='proceed')
    config.add_view(social.login_success, context = SocialLoginSuccessful, permission = NO_PERMISSION_REQUIRED)
    config.add_view(social.login_failure, context = SocialLoginFailed, permission = NO_PERMISSION_REQUIRED)

    config.add_view(social.auth_required_view, context = social.RequiresLoginException, permission = NO_PERMISSION_REQUIRED)
    config.add_view(social.auth_required_view, context = HTTPForbidden, permission = NO_PERMISSION_REQUIRED)

    config.add_view(imp.company_import_start    , context = angellist.SocialResource, permission='import')
    config.add_view(imp.company_import          , context = angellist.SocialResource, name = 'import'   , permission='import')
    config.add_view(imp.company_import_list     , context = angellist.SocialResource, name = 'list'     , renderer = "ufostart:templates/company/import/list.html", permission='import')
    config.add_view(imp.company_import_confirm  , context = angellist.SocialResource, name = 'confirm'  , permission='import')