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

    def loginUser(self, request, profile):
        params = {'Profile': [profile]}
        if not request.root.user.isAnon():
            params['token'] = request.root.user.token
        try:
            user = SocialConnectProc(request, params)
        except DBNotification, e:
            log.error("UNHANDLED DB MESSAGE: %s", e.message)
            return None
        else:
            return user.toJSON()

    def loginCallback(self, request):
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
                profile = self.getProfileFromData(token, data)
                return self.loginUser(request, profile)

    def getAuthCode(self, request): raise NotImplementedError
    def getTokenProfile(self, content): raise NotImplementedError
    def getProfileFromData(self, token, data): raise NotImplementedError
