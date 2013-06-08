import logging
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client, Token
from pyramid.decorator import reify
from pyramid.view import view_config
import simplejson
from ufostart.website.apps.social import SocialSettings, SocialNetworkException, SocialLoginSuccessful, assemble_profile_procs

log = logging.getLogger(__name__)






class TwitterSettings(SocialSettings):
    getCodeEndpoint = "https://api.twitter.com/oauth/request_token"
    codeEndpoint = "https://api.twitter.com/oauth/authorize"
    tokenEndpoint = "https://api.twitter.com/oauth/access_token"
    profileEndpoint = "https://api.twitter.com/1.1/users/show.json"

    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)


@view_config(context = TwitterSettings)
def redirect_view(context, request):
    params = {'oauth_callback':request.rld_url(traverse=[context.type, 'cb'], with_query = False)}

    client = Client(context.consumer)
    resp, data = client.request(context.getCodeEndpoint, method="POST",body=urllib.urlencode(params))
    result = dict(parse_qsl(data))
    token = result.get("oauth_token")
    secret = result.get("oauth_token_secret")

    if resp.status != 200 or not (token and secret):
        raise SocialNetworkException(data)
    request.session['SOCIAL_TOKEN_{}'.format(context.type)] = Token(token, secret)

    params = urllib.urlencode({'oauth_token': token})
    request.fwd_raw("{}?{}".format(context.codeEndpoint, params))


def token_func(context, request):
    tokenSecret = request.session.pop('SOCIAL_TOKEN_{}'.format(context.type))
    verifier = request.params.get('oauth_verifier')
    if not (tokenSecret and verifier):
        raise SocialNetworkException()
    tokenSecret.set_verifier(verifier)

    client = Client(context.consumer, tokenSecret)
    return client.request(context.tokenEndpoint, method="POST", headers={'Accept':'application/json'})


def profile_func(content, context, request):
    result = dict(parse_qsl(content))

    token = result.get('oauth_token')
    secret  = result.get('oauth_token_secret')
    user_id = result.get('user_id')
    if not (token and secret and user_id):
        raise SocialNetworkException()

    token = Token(token, secret)
    client = Client(context.consumer, token, **context.http_options)
    return token, client.request('{}?user_id={}'.format(context.profileEndpoint, user_id), method="GET")


def parse_profile_func(token, data, context, request):
    profile = simplejson.loads(data)
    request.rld_url(action = "email")

    #
    # return SocialNetworkProfileModel({
    #     'type': SOCIAL_NETWORK_TYPES_REVERSE[context.type]
    #     , 'id':profile['id']
    #     , 'accessToken':token.key
    #     , 'secret':token.secret
    #     , 'picture': profile['profile_image_url_https']
    #     , 'name': u"{first_name} {last_name}".format(**profile)
    # })


get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)

@view_config(context = TwitterSettings, name="cb")
def callback_view(context, request):
    profile = get_profile(context, request)
    raise SocialLoginSuccessful(profile)
