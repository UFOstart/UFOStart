import logging, simplejson, urllib
from urlparse import parse_qsl
from httplib2 import Http
from ufostart.website.apps.models.auth import SOCIAL_NETWORK_TYPES_REVERSE
from ufostart.website.apps.social import SocialSettings

log = logging.getLogger(__name__)

class FacebookSettings(SocialSettings):
    getCodeEndpoint = "https://www.facebook.com/dialog/oauth"
    codeEndpoint = "https://graph.facebook.com/oauth/access_token"
    profileEndpoint = "https://graph.facebook.com/me"
    def get_pic_url(self, network_id):
        return "https://graph.facebook.com/%s/picture" % network_id


    def loginStart(self, request, redirect_route, redirect_kwargs):
        params = {'client_id':self.appid, 'scope':'email'
                    , 'redirect_uri':request.fwd_url(redirect_route, network = self.type, **redirect_kwargs)
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))

    def getAuthCode(self, request, redirect_route, redirect_kwargs):
        code = request.params.get("code")
        params = {'client_id':self.appid, 'client_secret':self.appsecret
                    , 'redirect_uri':request.fwd_url(redirect_route, network = self.type, **redirect_kwargs)
                    , 'code':code}
        h = Http(**self.http_options)
        url = "{}?{}".format(self.codeEndpoint, urllib.urlencode(params))
        return h.request(url, method="GET")


    def getTokenProfile(self, content):
        h = Http(**self.http_options)
        result = dict(parse_qsl(content))
        access_token = result['access_token']
        return access_token, h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET" )


    def getProfileFromData(self, token, data):
        profile = simplejson.loads(data)
        return {
                    'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                    , 'id':profile['id']
                    , 'accessToken':token
                    , 'picture': self.get_pic_url(profile['id'])
                    , 'email': profile['email']
                    , 'name': profile['name']
                }
