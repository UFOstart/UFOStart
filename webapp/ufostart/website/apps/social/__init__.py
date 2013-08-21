import logging, simplejson
from pyramid.security import Everyone, Allow, Authenticated

__all__ = ['AbstractSocialResource', 'SocialNetworkProfileModel', 'angellist', 'facebook', 'linkedin', 'twitter', 'xing'
    , 'SocialLoginSuccessful', 'SocialLoginFailed', 'UserRejectedNotice', 'InvalidSignatureException', 'SocialNetworkException'
    , 'ExpiredException', 'CustomProcessException']


log = logging.getLogger(__name__)

class SocialResult(Exception):
    def get_redirection(self, request):
        redirections = request.session.pop_flash('redirections')
        route = redirections[-1] if redirections else request.root.home_url
        return route


class SocialLoginFailed(SocialResult):
    def __init__(self, msg):
        self.message = msg

class UserRejectedNotice(SocialLoginFailed): pass
class InvalidSignatureException(SocialLoginFailed):pass
class SocialNetworkException(SocialLoginFailed):pass
class ExpiredException(SocialLoginFailed):pass
class CustomProcessException(SocialLoginFailed):pass


class SocialLoginSuccessful(SocialResult):
    def __init__(self, profile):
        self.profile = profile





class AbstractSocialResource(object):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'import')]
    @property
    def request(self):
        return self.__parent__.request

    def __init__(self, parent, name, settings):
        self.__parent__ = parent
        self.__name__ = name
        self.settings = settings

    def toPublicJSON(self, stringify = True):
        result = {'appId':self.settings.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result

    def start_process(self, request):
        furl = request.params.get('furl')
        if furl:
            request.session.flash(furl, 'redirections')



def assemble_profile_procs(token_func, profile_func, parse_profile_func):
    """after redirect, this will do some more API magic and return the social profile"""
    def get_profile_inner(context, request):
        settings = context.settings
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice("You need to accept {} permissions to use {}.".format(settings.network.title(), request.globals.project_name))
            else:
                raise SocialNetworkException("{} login failed.".format(context.network.title()))
        resp, content = token_func(context, request)
        if resp.status not in [200,201]:
            raise SocialNetworkException("{} login failed.".format(settings.network.title()))
        else:
            token, (resp, data) = profile_func(content, context, request)
            if 400 <= resp.status < 500:
                raise ExpiredException("{} login failed.".format(settings.network.title()))
            if resp.status not in [200,201]:
                raise SocialNetworkException("{} login failed.".format(settings.network.title()))
            else:
                return parse_profile_func(token, data, context, request)
    return get_profile_inner


from . import linkedin, facebook, xing, angellist

def includeme(config):
    config.add_view(linkedin.redirect_view  , context = linkedin.SocialResource)
    config.add_view(linkedin.callback_view  , context = linkedin.SocialResource, name = 'cb')

    config.add_view(facebook.redirect_view  , context = facebook.SocialResource)
    config.add_view(facebook.callback_view  , context = facebook.SocialResource, name = 'cb')

    config.add_view(xing.redirect_view      , context = xing.SocialResource)
    config.add_view(xing.callback_view      , context = xing.SocialResource, name = 'cb')
