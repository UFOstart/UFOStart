import base64, logging
from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.messages import GenericErrorMessage

from ufostart.website.apps.models.auth import RefreshAccessTokenProc, SocialConnectProc, SOCIAL_NETWORK_TYPES_REVERSE
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException, InvalidSignatureException


log = logging.getLogger(__name__)


def fb_token_refresh(context, request):
    json_body = request.json_body
    isLogin = request.user.facebookId != json_body.get("facebookId")
    request.user.accessToken = json_body.get('accessToken')
    if not request.user.isAnon():
        try:
            RefreshAccessTokenProc(request, {'token':request.user.token, 'accessToken':json_body.get('accessToken')})
        except (DBNotification, DBException), e:
            pass
    return {"success":True, "isLogin": isLogin}


def login_user(request, profile):
    params = {'Profile': [profile]}
    if not request.root.user.isAnon():
        params['token'] = request.root.user.token
    try:
        user = SocialConnectProc(request, params)
    except DBNotification, e:
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        return None
    else:
        return user.toJSON()


def get_social_profile(request, networkSettings, original_route, error_route):
    network = networkSettings.type
    try:
        profile = networkSettings.profileCallback(request, original_route)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to use {}.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd(error_route)
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} login failed.".format(network.title())), "generic_messages")
        request.fwd(error_route)
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} login failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd(error_route)
        else:
            return profile



def social_login_start(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    return networkSettings.loginStart(request, 'website_social_login_callback')

def social_login_callback(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    profile = get_social_profile(request, networkSettings, original_route = 'website_social_login_callback', error_route = "website_index")
    user = login_user(request, profile)
    route, args, kwargs = request.root.getPostLoginUrlParams()
    request.fwd(route, *args, **kwargs)