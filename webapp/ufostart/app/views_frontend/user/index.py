import logging
from hnc.apiclient.backend import DBNotification, ClientTokenProc
from hnc.forms.messages import GenericErrorMessage
from pyramid.response import Response
from ufostart.app.models.auth import SocialNetworkProfileModel, SOCIAL_NETWORK_TYPES_REVERSE, SOCIAL_NETWORK_TYPES

log = logging.getLogger(__name__)

def home(context, request):
    return {}

def user(context, request):
    return {}

def browse(context, request):
    return {}


def connect_user(context, request, profile):
    if isinstance(profile, SocialNetworkProfileModel):
        profile = profile.unwrap(sparse = True)
        if profile.get('network') and not profile.get('type'):
            profile['type'] = SOCIAL_NETWORK_TYPES_REVERSE[profile['network']]
        elif not profile.get('network') and profile.get('type'):
            profile['network'] = SOCIAL_NETWORK_TYPES[profile['type']]

    connectProc = ClientTokenProc("/web/user/{}".format(profile['network']))
    params = {'Profile': [profile], "token": context.user.token}
    return connectProc(request, params)



def login_success(exc, request):
    try:
        user = connect_user(request.root, request, exc.profile)
    except DBNotification, e:
        if e.message == 'NO_USER_WITH_THIS_ACCOUNT':
            return Response("Resource Found!", 302, headerlist = [('location', request.fwd_url(request.context.__parent__))])
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        request.session.flash(GenericErrorMessage(e.message), "generic_messages")

    route = request.fwd_url(request.context.__parent__)
    return Response("Resource Found!", 302, headerlist = [('location', route)])


def login_failure(exc, request):
    request.session.flash(GenericErrorMessage(exc.message), "generic_messages")
    route = request.fwd_url(request.context.__parent__)
    return Response("Resource Found!", 302, headerlist = [('location', route)])
