import logging
from hnc.apiclient.backend import DBNotification, DBException
from ufostart.website.apps.models.auth import RefreshAccessTokenProc, SocialConnectProc

log = logging.getLogger(__name__)


def fb_accept_requests(context, request):
    # this needs to be client initiated, as we cant decide serverside if user has accepted facebook login, only javascript really knows
    request.session.pop_flash("fb_requests")
    return {'success': True}



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

def extract_fb_data(request):
    profile = request.json_body['profile']
    try:
        values = {
            'name': profile['name']
            , 'pwd': 'Popov2010'
            , 'email': profile['email']
            , 'Profile': [{
                'id': profile['id']
                , 'type':'FB'
                , 'picture': profile['picture']
                , 'accessToken': request.json_body['authResponse']['accessToken']
                , 'email': profile['email']
                , 'name': profile['name']
            }]
        }
    except KeyError, e:
        return None
    else:
        user = request.root.user
        if not user.isAnon():
            values['name'] = user.name
            values['email'] = user.email
        return values


def fb_login(context, request):
    result = {'success': False}
    values = extract_fb_data(request)
    if not values: return result
    try:
        user = SocialConnectProc(request, values)
    except DBNotification, e:
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        return {'success':False, 'message': e.message}
    result['success'] = True
    return result


