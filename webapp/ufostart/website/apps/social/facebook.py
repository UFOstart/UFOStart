import logging, simplejson, urllib
from urlparse import parse_qsl
from httplib2 import Http
from pyramid.view import view_config
from ufostart.website.apps.social import AbstractSocialResource, SocialNetworkProfileModel, SocialLoginSuccessful, assemble_profile_procs

log = logging.getLogger(__name__)




class SocialResource(AbstractSocialResource):
    getCodeEndpoint = "https://www.facebook.com/dialog/oauth"
    codeEndpoint = "https://graph.facebook.com/oauth/access_token"
    profileEndpoint = "https://graph.facebook.com/me"
    def get_pic_url(self, network_id):
        return "https://graph.facebook.com/%s/picture" % network_id




def redirect_view(context, request):
    settings = context.settings
    context.start_process(request)
    params = {'client_id':settings.appid, 'scope':'email'
                , 'redirect_uri':request.resource_url(request.context, 'cb')
             }
    request.fwd_raw("{}?{}".format(context.getCodeEndpoint, urllib.urlencode(params)))



def token_func(context, request):
    settings = context.settings
    code = request.params.get("code")
    params = {'client_id':settings.appid, 'client_secret':settings.appsecret
                , 'redirect_uri':request.resource_url(request.context, 'cb')
                , 'code':code}
    h = Http(**settings.http_options)
    url = "{}?{}".format(context.codeEndpoint, urllib.urlencode(params))
    return h.request(url, method="GET")


def profile_func(content, context, request):
    settings = context.settings
    h = Http(**settings.http_options)
    result = dict(parse_qsl(content))
    access_token = result['access_token']
    return access_token, h.request('{}?{}'.format(context.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET" )


def parse_profile_func(token, data, context, request):
    settings = context.settings
    profile = simplejson.loads(data)
    return SocialNetworkProfileModel(
                network = settings.network
                , id = profile['id']
                , accessToken = token
                , picture = context.get_pic_url(profile['id'])
                , email = profile['email']
                , name = profile['name']
            )

get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)


def callback_view(context, request):
    settings = context.settings
    profile = get_profile(context, request)
    request.session['SOCIAL_BACKUP_{}'.format(settings.network)] = profile
    raise SocialLoginSuccessful(profile)