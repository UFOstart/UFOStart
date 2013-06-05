import base64, logging
from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.messages import GenericErrorMessage

from ufostart.website.apps.models.procs import RefreshAccessTokenProc, SocialConnectProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


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


def social_login(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    profile = networkSettings.getSocialProfile(request, request.fwd_url("website_index"))

    user = login_user(request, profile)
    route, args, kwargs = request.root.getPostLoginUrlParams()
    request.fwd(route, *args, **kwargs)