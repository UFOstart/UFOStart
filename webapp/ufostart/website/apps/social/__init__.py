import logging, simplejson
from hnc.apiclient import Mapping, TextField


log = logging.getLogger(__name__)


class SocialLoginFailed(Exception):
    def __init__(self, msg):
        self.message = msg

class UserRejectedNotice(SocialLoginFailed): pass
class InvalidSignatureException(SocialLoginFailed):pass
class SocialNetworkException(SocialLoginFailed):pass
class ExpiredException(SocialLoginFailed):pass
class CustomProcessException(SocialLoginFailed):pass


class SocialLoginSuccessful(Exception):
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




def assemble_profile_procs(token_func, profile_func, parse_profile_func):
    """after redirect, this will do some more API magic and return the social profile"""
    def get_profile_inner(context, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice("You need to accept {} permissions to use {}.".format(context.type.title(), request.globals.project_name))
            else:
                raise SocialNetworkException("{} login failed.".format(context.type.title()))
        resp, content = token_func(context, request)
        if resp.status not in [200,201]:
            raise SocialNetworkException("{} login failed.".format(context.type.title()))
        else:
            token, (resp, data) = profile_func(content, context, request)
            if 400 <= resp.status < 500:
                raise ExpiredException("{} login failed.".format(context.type.title()))
            if resp.status not in [200,201]:
                raise SocialNetworkException("{} login failed.".format(context.type.title()))
            else:
                return parse_profile_func(token, data, context, request)
    return get_profile_inner





class SocialSettings(object):
    http_options = {'disable_ssl_certificate_validation' : True}
    default_picture = "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def __init__(self, network, appid, appsecret):
        self.network = network
        self.appid = appid
        self.appsecret = appsecret

    def toPublicJSON(self, stringify = True):
        result = {'appId':self.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result
