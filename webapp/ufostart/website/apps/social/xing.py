import logging
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client, Token
from pyramid.decorator import reify
from pyramid.view import view_config
import simplejson
from ufostart.website.apps.social import AbstractSocialResource, SocialNetworkException, SocialNetworkProfileModel, assemble_profile_procs, SocialLoginSuccessful

log = logging.getLogger(__name__)


class SocialResource(AbstractSocialResource):
    getCodeEndpoint = "https://api.xing.com/v1/request_token"
    codeEndpoint = "https://api.xing.com/v1/authorize"
    tokenEndpoint = "https://api.xing.com/v1/access_token"
    profileEndpoint = "https://api.xing.com/v1/users/me"

    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)


@view_config(context = SocialResource)
def redirect_view(context, request):
    context.start_process(request)
    params = {'oauth_callback':request.rld_url(traverse=[context.network, 'cb'], with_query = False)}

    client = Client(context.consumer)
    resp, data = client.request(context.getCodeEndpoint, method="POST",body=urllib.urlencode(params), headers={'Accept':'application/json'})
    result = dict(parse_qsl(data))
    token = result.get("oauth_token")
    secret = result.get("oauth_token_secret")

    if resp.status != 201 or not (token and secret):
        raise SocialNetworkException(data)
    request.session['SOCIAL_TOKEN_{}'.format(context.network)] = Token(token, secret)

    params = urllib.urlencode({'oauth_token': token})
    request.fwd_raw("{}?{}".format(context.codeEndpoint, params))


def token_func(context, request):
    tokenSecret = request.session.pop('SOCIAL_TOKEN_{}'.format(context.network))
    verifier = request.params.get('oauth_verifier')
    if not (tokenSecret and verifier):
        raise SocialNetworkException("{} Login Failed".format(context.network))
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

    accessToken = Token(token, secret)
    client = Client(context.consumer, accessToken)
    return accessToken, client.request('{}'.format(context.profileEndpoint), method="GET")



def getBestProfilePicture(context, pictures):
    preference = ["maxi_thumb", "large", "thumb", "medium_thumb", "mini_thumb"]
    for name in preference:
        if pictures.get('name'):
            return pictures.get('name')
    return context.default_picture

def parse_profile_func(tokenSecret, data, context, request):
    profiles = simplejson.loads(data)
    profile = profiles.get('users', [])
    if not profile: return None
    profile = profile[0]

    picture = getBestProfilePicture(context, profile.get('photo_urls', []))

    return SocialNetworkProfileModel(
            network = context.network
            , id = profile['id']
            , accessToken = tokenSecret.key
            , secret = tokenSecret.secret
            , picture = picture
            , email = profile['active_email']
            , name = u"{first_name} {last_name}".format(**profile)
        )

get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)

@view_config(context = SocialResource, name="cb")
def callback_view(context, request):
    profile = get_profile(context, request)
    raise SocialLoginSuccessful(profile)