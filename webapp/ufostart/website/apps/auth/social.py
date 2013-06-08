import logging
from hnc.apiclient.backend import DBNotification
from hnc.forms.messages import GenericErrorMessage
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import view_config

from ufostart.website.apps.models.procs import SocialConnectProc
from ufostart.website.apps.social import SocialNetworkProfileModel, SocialLoginSuccessful, SocialLoginFailed


log = logging.getLogger(__name__)


def login_user(context, request, profile):
    if isinstance(profile, SocialNetworkProfileModel):
        profile = profile.unwrap(sparse = True)
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


@view_config(context = SocialLoginSuccessful)
def login_success(exc, request):
    login_user(request.root, request, exc.profile)
    route = request.matched_route.name.rsplit('_', 1)[0]
    params = request.matchdict.copy()
    params.pop('traverse')
    route = request.fwd_url(route, **params)
    return Response("Resource Found!", 302, headerlist = [('location', route)])


@view_config(context = SocialLoginFailed)
def login_failure(exc, request):
    request.session.flash(GenericErrorMessage(exc.message), "generic_messages")

    route = request.matched_route.name.rsplit('_', 1)[0]
    params = request.matchdict.copy()
    params.pop('traverse')
    route = request.fwd_url(route, **params)
    return Response("Resource Found!", 302, headerlist = [('location', route)])






class RequiresLoginException(Exception):
    def __init__(self, template):
        self.template = template

@view_config(context = RequiresLoginException)
def auth_required_view(exc, request):
    # TODO: can this be a class based view to use as email login handler?
    return render_to_response(exc.template, {}, request)


def require_login(template):
    def require_login_real(fn):
        def require_login_inner(context, request):
            if request.root.user.isAnon():
                raise RequiresLoginException(template)
            else:
                return fn(context, request)
        return require_login_inner
    return require_login_real