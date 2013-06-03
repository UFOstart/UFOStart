import logging, simplejson
from hnc.apiclient.backend import DBNotification
from ufostart.website.apps.models.auth import SocialConnectProc

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

    def requiresAction(self):
        return False

    # EXPOSED Functions
    def profileCallback(self, request, redirect_route):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None
        resp, content = self.getAuthCode(request, redirect_route)
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

    def loginStart(self, request, redirect_route): raise NotImplementedError
    def getAuthCode(self, request, redirect_route): raise NotImplementedError
    def getTokenProfile(self, content): raise NotImplementedError
    def getProfileFromData(self, token, data): raise NotImplementedError
