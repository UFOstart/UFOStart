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

    def loginStart(self, request):
        params = {'response_type':"code"
                    , 'client_id':self.appid
                    , 'state': request.session.get_csrf_token()
                    , 'redirect_uri':request.rld_url(action='cb', with_query = False)
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))


    def getAuthCode(self, request):
        code = request.params.get("code")
        state = request.params.get("state")
        if not code or state != request.session.get_csrf_token():
            return False

        params = {'grant_type':'authorization_code', 'code':code
                    , 'redirect_uri':request.rld_url(action='cb', with_query = False)
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
                , 'picture': profile.get('pictureUrl', self.default_picture)
                , 'email': profile['emailAddress']
                , 'name': u"{firstName} {lastName}".format(**profile)
            }
