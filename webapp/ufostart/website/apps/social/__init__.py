import logging, simplejson
from hnc.apiclient import Mapping, TextField, DictField
from pyramid.security import Everyone, Allow

__all__ = ['AbstractSocialResource', 'SocialNetworkProfileModel', 'angellist', 'facebook', 'linkedin', 'twitter', 'xing'
    , 'SocialLoginSuccessful', 'SocialLoginFailed', 'UserRejectedNotice', 'InvalidSignatureException', 'SocialNetworkException'
    , 'ExpiredException', 'CustomProcessException']


log = logging.getLogger(__name__)

class SocialResult(Exception):
    def get_redirection(self, request):
        redirections = request.session.pop_flash('redirections')
        if redirections:
            route = redirections[-1]
        else:
            route = request.matched_route.name.rsplit('_', 1)[0]
            params = request.matchdict.copy()
            params.pop('traverse')
            route = request.fwd_url(route, **params)
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



class SocialNetworkProfileModel(Mapping):
    id = TextField()
    network = TextField()
    picture = TextField()
    name = TextField()
    email = TextField()
    accessToken = TextField()
    secret = TextField()
    original = DictField()



class AbstractSocialResource(object):
    __acl__ = [(Allow, Everyone, 'view')]
    http_options = {'disable_ssl_certificate_validation' : True}
    default_picture = "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def __init__(self, network, appid, appsecret, **kwargs):
        self.__name__ = network
        self.network = network
        self.appid = appid
        self.appsecret = appsecret
        for k,v in kwargs.items():
            setattr(self, k, v)

    def toPublicJSON(self, stringify = True):
        result = {'appId':self.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result

    def start_process(self, request):
        furl = request.params.get('furl')
        if furl:
            request.session.flash(furl, 'redirections')



def assemble_profile_procs(token_func, profile_func, parse_profile_func):
    """after redirect, this will do some more API magic and return the social profile"""
    def get_profile_inner(context, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice("You need to accept {} permissions to use {}.".format(context.network.title(), request.globals.project_name))
            else:
                raise SocialNetworkException("{} login failed.".format(context.network.title()))
        resp, content = token_func(context, request)
        if resp.status not in [200,201]:
            raise SocialNetworkException("{} login failed.".format(context.network.title()))
        else:
            token, (resp, data) = profile_func(content, context, request)
            if 400 <= resp.status < 500:
                raise ExpiredException("{} login failed.".format(context.network.title()))
            if resp.status not in [200,201]:
                raise SocialNetworkException("{} login failed.".format(context.network.title()))
            else:
                return parse_profile_func(token, data, context, request)
    return get_profile_inner


