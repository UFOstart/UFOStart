import logging
import urllib
from httplib2 import Http
import simplejson
from ufostart.website.apps.models.auth import SocialNetworkProfileModel
from ufostart.website.apps.social import AbstractSocialResource, SocialLoginSuccessful, assemble_profile_procs

log = logging.getLogger(__name__)




class SocialResource(AbstractSocialResource):
    getCodeEndpoint = "https://www.linkedin.com/uas/oauth2/authorization"
    getTokenEndpoint = "https://www.linkedin.com/uas/oauth2/accessToken"
    profileEndpoint = "https://api.linkedin.com/v1/people/~:(id,first-name,last-name,picture-url,email-address)"


def redirect_view(context, request):
    settings = context.settings
    context.start_process(request)
    params = {'response_type':"code"
                , 'client_id':settings.appid
                , 'state': request.session.get_csrf_token()
                , 'scope':'r_basicprofile r_emailaddress r_network r_fullprofile r_contactinfo w_messages'
                , 'redirect_uri':request.resource_url(request.context, 'cb')
             }
    request.fwd_raw("{}?{}".format(context.getCodeEndpoint, urllib.urlencode(params)))



def token_func(context, request):
    settings = context.settings
    code = request.params.get("code")
    state = request.params.get("state")
    if not code or state != request.session.get_csrf_token():
        return False

    params = {'grant_type':'authorization_code', 'code':code
                , 'redirect_uri':request.resource_url(request.context, 'cb')
                , 'client_id':settings.appid, 'client_secret':settings.appsecret
             }

    h = Http()
    return h.request( "{}?{}".format(context.getTokenEndpoint, urllib.urlencode(params)), method="POST", body = {} )

def profile_func(content, context, request):
    settings = context.settings
    h = Http()
    result = simplejson.loads(content)
    access_token = result['access_token']
    return access_token, h.request('{}?{}'.format(context.profileEndpoint, urllib.urlencode({'oauth2_access_token':access_token})), method="GET" , headers = {'x-li-format':'json'})

def parse_profile_func(token, data, context, request):
    settings = context.settings
    profile = simplejson.loads(data)
    return SocialNetworkProfileModel(
            network = settings.network
            , id = profile['id']
            , accessToken = token
            , picture = profile.get('pictureUrl', settings.default_picture)
            , email = profile['emailAddress']
            , name = u"{firstName} {lastName}".format(**profile)
        )

get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)


def callback_view(context, request):
    profile = get_profile(context, request)
    raise SocialLoginSuccessful(profile)