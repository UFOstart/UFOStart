import logging, simplejson, urllib
from urlparse import parse_qsl
from httplib2 import Http
from pyramid.view import view_config
from ufostart.website.apps.social import SocialSettings, SocialNetworkProfileModel, SocialLoginSuccessful, assemble_profile_procs

log = logging.getLogger(__name__)




class SocialResource(SocialSettings):
    getCodeEndpoint = "https://www.facebook.com/dialog/oauth"
    codeEndpoint = "https://graph.facebook.com/oauth/access_token"
    profileEndpoint = "https://graph.facebook.com/me"
    def get_pic_url(self, network_id):
        return "https://graph.facebook.com/%s/picture" % network_id



@view_config(context = SocialResource)
def redirect_view(context, request):
    params = {'client_id':context.appid, 'scope':'email'
                , 'redirect_uri':request.rld_url(traverse=[context.network, 'cb'], with_query = False)
             }
    request.fwd_raw("{}?{}".format(context.getCodeEndpoint, urllib.urlencode(params)))



def token_func(context, request):
    code = request.params.get("code")
    params = {'client_id':context.appid, 'client_secret':context.appsecret
                , 'redirect_uri':request.rld_url(action='cb', with_query = False)
                , 'code':code}
    h = Http(**context.http_options)
    url = "{}?{}".format(context.codeEndpoint, urllib.urlencode(params))
    return h.request(url, method="GET")


def profile_func(content, context, request):
    h = Http(**context.http_options)
    result = dict(parse_qsl(content))
    access_token = result['access_token']
    return access_token, h.request('{}?{}'.format(context.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET" )


def parse_profile_func(token, data, context, request):
    profile = simplejson.loads(data)
    return SocialNetworkProfileModel(
                network = context.network
                , id = profile['id']
                , accessToken = token
                , picture = context.get_pic_url(profile['id'])
                , email = profile['email']
                , name = profile['name']
            )

get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)

@view_config(context = SocialResource, name="cb")
def callback_view(context, request):
    profile = get_profile(context, request)
    raise SocialLoginSuccessful(profile)