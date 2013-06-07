import base64
import hashlib
import hmac
import logging
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client, Token
from httplib2 import Http
from pyramid.decorator import reify
import simplejson
from ufostart.website.apps.models.auth import SOCIAL_NETWORK_TYPES_REVERSE, SocialNetworkProfileModel
from ufostart.website.apps.social import SocialSettings, InvalidSignatureException, SocialNetworkException

log = logging.getLogger(__name__)


class XingSettings(SocialSettings):
    getCodeEndpoint = "https://api.xing.com/v1/request_token"
    codeEndpoint = "https://api.xing.com/v1/authorize"
    tokenEndpoint = "https://api.xing.com/v1/access_token"
    profileEndpoint = "https://api.xing.com/v1/users/me"

    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)



    def loginStart(self, request):
        params = {'oauth_callback':request.rld_url(action='cb', with_query = False)}

        client = Client(self.consumer)
        resp, data = client.request(self.getCodeEndpoint, method="POST",body=urllib.urlencode(params), headers={'Accept':'application/json'})
        result = dict(parse_qsl(data))
        token = result.get("oauth_token")
        secret = result.get("oauth_token_secret")

        if resp.status != 201 or not (token and secret):
            raise SocialNetworkException(data)
        request.session['SOCIAL_TOKEN_{}'.format(self.type)] = Token(token, secret)

        params = urllib.urlencode({'oauth_token': token})
        request.fwd_raw("{}?{}".format(self.codeEndpoint, params))


    def getAuthCode(self, request):
        tokenSecret = request.session.pop('SOCIAL_TOKEN_{}'.format(self.type))
        verifier = request.params.get('oauth_verifier')
        if not (tokenSecret and verifier):
            raise SocialNetworkException()
        tokenSecret.set_verifier(verifier)

        client = Client(self.consumer, tokenSecret)
        return client.request(self.tokenEndpoint, method="POST", headers={'Accept':'application/json'})


    def getTokenProfile(self, content):
        result = dict(parse_qsl(content))

        token = result.get('oauth_token')
        secret  = result.get('oauth_token_secret')
        user_id = result.get('user_id')
        if not (token and secret and user_id):
            raise SocialNetworkException()

        accessToken = Token(token, secret)
        client = Client(self.consumer, accessToken)
        return accessToken, client.request('{}'.format(self.profileEndpoint), method="GET")

    def getBestProfilePicture(self, pictures):
        preference = ["maxi_thumb", "large", "thumb", "medium_thumb", "mini_thumb"]
        for name in preference:
            if pictures.get('name'):
                return pictures.get('name')
        return self.default_picture

    def getProfileFromData(self, tokenSecret, data, request):
        profiles = simplejson.loads(data)
        profile = profiles.get('users', [])
        if not profile: return None
        profile = profile[0]

        picture = self.getBestProfilePicture(profile.get('photo_urls', []))

        return SocialNetworkProfileModel(
                type = SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                , id = profile['id']
                , accessToken = tokenSecret.key
                , secret = tokenSecret.secret
                , picture = picture
                , email = profile['active_email']
                , name = u"{first_name} {last_name}".format(**profile)
            )
