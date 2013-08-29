import logging
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Client, Token
import simplejson
from ufostart.apps.social import AbstractSocialResource, SocialNetworkException, assemble_profile_procs, SocialLoginSuccessful
from ufostart.models.auth import SocialNetworkProfileModel

log = logging.getLogger(__name__)


class SocialResource(AbstractSocialResource):
    getCodeEndpoint = "https://api.xing.com/v1/request_token"
    codeEndpoint = "https://api.xing.com/v1/authorize"
    tokenEndpoint = "https://api.xing.com/v1/access_token"
    profileEndpoint = "https://api.xing.com/v1/users/me"





def redirect_view(context, request):
    settings = context.settings
    context.start_process(request)
    params = {'oauth_callback':request.resource_url(request.context, 'cb')}

    client = Client(settings.consumer)
    resp, data = client.request(context.getCodeEndpoint, method="POST",body=urllib.urlencode(params), headers={'Accept':'application/json'})
    result = dict(parse_qsl(data))
    token = result.get("oauth_token")
    secret = result.get("oauth_token_secret")

    if resp.status != 201 or not (token and secret):
        raise SocialNetworkException(data)
    request.session['SOCIAL_TOKEN_{}'.format(settings.network)] = Token(token, secret)

    params = urllib.urlencode({'oauth_token': token})
    request.fwd_raw("{}?{}".format(context.codeEndpoint, params))


def token_func(context, request):
    settings = context.settings
    tokenSecret = request.session.pop('SOCIAL_TOKEN_{}'.format(settings.network))
    verifier = request.params.get('oauth_verifier')
    if not (tokenSecret and verifier):
        raise SocialNetworkException("{} Login Failed".format(settings.network))
    tokenSecret.set_verifier(verifier)

    client = Client(settings.consumer, tokenSecret)
    return client.request(context.tokenEndpoint, method="POST", headers={'Accept':'application/json'})


def profile_func(content, context, request):
    settings = context.settings
    result = dict(parse_qsl(content))

    token = result.get('oauth_token')
    secret  = result.get('oauth_token_secret')
    user_id = result.get('user_id')
    if not (token and secret and user_id):
        raise SocialNetworkException()

    accessToken = Token(token, secret)
    client = Client(settings.consumer, accessToken)
    return accessToken, client.request('{}'.format(context.profileEndpoint), method="GET")



def getBestProfilePicture(context, pictures):
    settings = context.settings
    preference = ["maxi_thumb", "large", "thumb", "medium_thumb", "mini_thumb"]
    for name in preference:
        if pictures.get('name'):
            return pictures.get('name')
    return settings.default_picture

def parse_profile_func(tokenSecret, data, context, request):
    settings = context.settings
    profiles = simplejson.loads(data)
    profile = profiles.get('users', [])
    if not profile: return None
    profile = profile[0]

    picture = getBestProfilePicture(context, profile.get('photo_urls', []))

    return SocialNetworkProfileModel(
            network = settings.network
            , id = profile['id']
            , accessToken = tokenSecret.key
            , secret = tokenSecret.secret
            , picture = picture
            , email = profile['active_email']
            , name = u"{first_name} {last_name}".format(**profile)
        )

get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)


def callback_view(context, request):
    profile = get_profile(context, request)
    raise SocialLoginSuccessful(profile)