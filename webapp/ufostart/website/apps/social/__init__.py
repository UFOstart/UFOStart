import logging, simplejson
from hnc.forms.messages import GenericErrorMessage

log = logging.getLogger(__name__)

class SocialNotice(Exception): pass
class UserRejectedNotice(SocialNotice): pass
class InvalidSignatureException(Exception):pass
class SocialNetworkException(Exception):pass

class SocialSettings(object):
    http_options = {'disable_ssl_certificate_validation' : True}
    def __init__(self, type, appid, appsecret):
        self.type = type
        self.appid = appid
        self.appsecret = appsecret

    def toPublicJSON(self, stringify = True):
        result = {'appId':self.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result

    def profileCallback(self, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None
        resp, content = self.getAuthCode(request)
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            result = simplejson.loads(content)
            return None
        else:
            token, (resp, data) = self.getTokenProfile(content)
            if resp.status == 500:
                raise SocialNetworkException()
            if resp.status != 200:
                result = simplejson.loads(data)
                return None
            else:
                return self.getProfileFromData(token, data)

    def loginStart(self, request): raise NotImplementedError
    def getAuthCode(self, request): raise NotImplementedError
    def getTokenProfile(self, content): raise NotImplementedError
    def getProfileFromData(self, token, data): raise NotImplementedError



    # EXPOSED Functions

    def getSocialProfile(self, request, error_url):
        action = request.matchdict['action']
        if action != 'cb':
            # this will redirect, per oauth to get the code
            self.loginStart(request)
        else:
            #after redirect, this will do some more API magic and return the social profile
            try:
                profile = self.profileCallback(request)
            except UserRejectedNotice, e:
                request.session.flash(GenericErrorMessage("You need to accept {} permissions to use {}.".format(self.type.title(), request.globals.project_name)), "generic_messages")
                request.fwd_raw(error_url)
            except SocialNetworkException, e:
                request.session.flash(GenericErrorMessage("{} login failed.".format(self.type.title())), "generic_messages")
                request.fwd_raw(error_url)
            else:
                if not profile:
                    request.session.flash(GenericErrorMessage("{} login failed. It seems the request expired. Please try again".format(self.type.title())), "generic_messages")
                    request.fwd_raw(error_url)
                else:
                    return profile