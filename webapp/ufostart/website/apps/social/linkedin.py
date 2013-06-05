import base64
import hashlib
import hmac
import logging
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client
from httplib2 import Http
import simplejson
from ufostart.website.apps.models.auth import SOCIAL_NETWORK_TYPES_REVERSE
from ufostart.website.apps.social import SocialSettings, InvalidSignatureException

log = logging.getLogger(__name__)


class LinkedinSettings(SocialSettings):
    getCodeEndpoint = "https://www.linkedin.com/uas/oauth2/authorization"
    codeEndpoint = "https://www.linkedin.com/uas/oauth2/accessToken"
    profileEndpoint = "https://api.linkedin.com/v1/people/~:(id,first-name,last-name,picture-url,email-address)"

    def loginStart(self, request, redirect_route):
        params = {'response_type':"code"
                    , 'client_id':self.appid
                    , 'state': request.session.get_csrf_token()
                    , 'redirect_uri':redirect_route
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))


    def getAuthCode(self, request, redirect_route):
        code = request.params.get("code")
        state = request.params.get("state")
        if not code or state != request.session.get_csrf_token():
            return False

        params = {'grant_type':'authorization_code', 'code':code
                    , 'redirect_uri':redirect_route
                    , 'client_id':self.appid, 'client_secret':self.appsecret
                 }

        h = Http(**self.http_options)
        return h.request( "{}?{}".format(self.codeEndpoint, urllib.urlencode(params)), method="POST", body = {} )


    def getTokenProfile(self, content):
        h = Http(**self.http_options)
        result = simplejson.loads(content)
        access_token = result['access_token']
        return access_token, h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'oauth2_access_token':access_token})), method="GET" , headers = {'x-li-format':'json'})


    def getProfileFromData(self, token, data):
        profile = simplejson.loads(data)
        return {
                'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                , 'id':profile['id']
                , 'accessToken':token
                , 'picture': profile.get('pictureUrl', "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm")
                , 'email': profile['emailAddress']
                , 'name': u"{firstName} {lastName}".format(**profile)
            }


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
__author__ = 'Martin'


