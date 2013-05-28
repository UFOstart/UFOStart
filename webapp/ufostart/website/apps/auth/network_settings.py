import base64, hashlib, hmac, urllib, simplejson
import logging
from urlparse import parse_qsl
from hnc.apiclient.backend import DBNotification
from hnc.tools.oauth import Client, Consumer
from httplib2 import Http
import uuid
from ufostart.website.apps.models.auth import SocialConnectProc, SOCIAL_NETWORK_TYPES_REVERSE, UserModel


log = logging.getLogger(__name__)

class SocialNotice(Exception): pass
class UserRejectedNotice(SocialNotice): pass
class InvalidSignatureException(Exception):pass


class SocialSettings(object):
    http_options = {}
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


class FacebookSettings(SocialSettings):
    getCodeEndpoint = "https://www.facebook.com/dialog/oauth"
    codeEndpoint = "https://graph.facebook.com/oauth/access_token"
    profileEndpoint = "https://graph.facebook.com/me"
    def get_pic_url(self, network_id):
        return "https://graph.facebook.com/%s/picture" % network_id


    def loginStart(self, request):
        params = {'client_id':self.appid, 'scope':'email'
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))

    def loginCallback(self, request):

        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None

        code = request.params.get("code")
        params = {'client_id':self.appid, 'client_secret':self.appsecret
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                    , 'code':code}
        h = Http(**self.http_options)
        url = "{}?{}".format(self.codeEndpoint, urllib.urlencode(params))

        resp, content = h.request(url, method="GET")
        if resp.status == 400:
            result = simplejson.loads(content)
            return None
        else:
            result = dict(parse_qsl(content))
            access_token = result['access_token']
            resp, content = h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET" )
            profile = simplejson.loads(content)

            data = {
                'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                , 'id':profile['id']
                , 'accessToken':access_token
                , 'picture': self.get_pic_url(profile['id'])
                , 'email': profile['email']
                , 'name': profile['name']
            }
            return self.loginUser(request, data)


class LinkedInSettings(SocialSettings):
    getCodeEndpoint = "https://www.linkedin.com/uas/oauth2/authorization"
    codeEndpoint = "https://www.linkedin.com/uas/oauth2/accessToken"
    profileEndpoint = "https://api.linkedin.com/v1/people/~:(id,first-name,last-name,picture-url,email-address)"

    def loginStart(self, request):
        params = {'response_type':"code"
                    , 'client_id':self.appid
                    , 'state': request.session.get_csrf_token()
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                    # , 'scope': " ".join(['r_basicprofile', 'r_fullprofile', 'r_emailaddress'])
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))

    def loginCallback(self, request):

        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None

        code = request.params.get("code")
        state = request.params.get("state")
        if not code or state != request.session.get_csrf_token():
            return False

        params = {'grant_type':'authorization_code', 'code':code
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                    , 'client_id':self.appid, 'client_secret':self.appsecret
                 }

        h = Http(**self.http_options)
        resp, content = h.request( "{}?{}".format(self.codeEndpoint, urllib.urlencode(params)), method="POST", body = {} )
        result = simplejson.loads(content)
        if resp.status == 400:
            return None
        else:
            access_token = result['access_token']
            resp, content = h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'oauth2_access_token':access_token})), method="GET" , headers = {'x-li-format':'json'})
            profile = simplejson.loads(content)

            data = {
                'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                , 'id':profile['id']
                , 'accessToken':access_token
                , 'picture': profile.get('pictureUrl', "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm")
                , 'email': profile['emailAddress']
                , 'name': "{firstName} {lastName}".format(**profile)
            }
            return self.loginUser(request, data)



    def requiresAction(self):
        return self.type == 'linkedin'

    def action(self, request, profile):
        cookie = request.cookies.get('linkedin_oauth_{}'.format(self.appid))
        values = simplejson.loads(urllib.unquote(cookie))
        sig = hmac.new(str(self.appsecret), digestmod=hashlib.sha1)
        for key in values['signature_order']:
            sig.update(values[key])
        if values['signature'] != base64.b64encode(sig.digest()):
            raise InvalidSignatureException()

        consumer = Consumer(self.appid, self.appsecret)
        client = Client(consumer)
        status, response = client.request('https://api.linkedin.com/uas/oauth/accessToken', method="POST",body="xoauth_oauth2_access_token={}".format(values['access_token']))
        res = dict(parse_qsl(response))
        profile['accessToken'] = res['oauth_token']
        profile['secret'] = res['oauth_token_secret']
        return profile





SOCIAL_CONECTORS_MAP = {'linkedin':LinkedInSettings, "facebook": FacebookSettings}