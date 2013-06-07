import base64
import hashlib
import hmac
import logging
import urllib
from urlparse import parse_qsl
from hnc.forms.formfields import REQUIRED, EmailField, BaseForm
from hnc.tools.oauth import Consumer, Client, Token
from httplib2 import Http
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
import simplejson
from ufostart.website.apps.social import SocialSettings, SocialNetworkException, AdditionalInformationRequired

log = logging.getLogger(__name__)

class TwitterEmailForm(BaseForm):
    id="TwitterEmail"
    label = ""
    fields=[EmailField('email', 'Email', REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        return {'success':True, 'redirect': request.fwd_url("")}




class TwitterSettings(SocialSettings):
    getCodeEndpoint = "https://api.twitter.com/oauth/request_token"
    codeEndpoint = "https://api.twitter.com/oauth/authorize"
    tokenEndpoint = "https://api.twitter.com/oauth/access_token"
    profileEndpoint = "https://api.twitter.com/1.1/users/show.json"

    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)



    def loginStart(self, request):
        params = {'oauth_callback':request.rld_url(action='cb', with_query = False)}

        client = Client(self.consumer)
        resp, data = client.request(self.getCodeEndpoint, method="POST",body=urllib.urlencode(params))
        result = dict(parse_qsl(data))
        token = result.get("oauth_token")
        secret = result.get("oauth_token_secret")

        if resp.status != 200 or not (token and secret):
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

        token = Token(token, secret)
        client = Client(self.consumer, token, **self.http_options)
        return token, client.request('{}?user_id={}'.format(self.profileEndpoint, user_id), method="GET")

    def customCallback(self, request):
        """
        as twitter does not return email address, in here we need to handle the page showing email request and also catch post back with form data
        """
        action = request.matchdict['action']
        if action == 'email':
            pass #TODO: implement twitter actual email collection
        raise HTTPNotFound()


    def getProfileFromData(self, token, data, request):
        profile = simplejson.loads(data)
        request.rld_url(action = "email")

        #
        # return SocialNetworkProfileModel({
        #     'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
        #     , 'id':profile['id']
        #     , 'accessToken':token.key
        #     , 'secret':token.secret
        #     , 'picture': profile['profile_image_url_https']
        #     , 'name': u"{first_name} {last_name}".format(**profile)
        # })
