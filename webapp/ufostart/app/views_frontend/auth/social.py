import logging
from pyramid.renderers import render_to_response
from pyramid.response import Response

from hnc.apiclient.backend import DBNotification
from hnc.forms.messages import GenericErrorMessage
from hnc.tools.request import JsonAwareRedirect

from ufostart.lib.html import slugify
from ufostart.app.models.auth import SOCIAL_NETWORK_TYPES, SOCIAL_NETWORK_TYPES_REVERSE
from ufostart.app.models.procs import LinkedinLoginProc
from ufostart.app.models.auth import SocialNetworkProfileModel

log = logging.getLogger(__name__)

def login_user(context, request, profile):
    if isinstance(profile, SocialNetworkProfileModel):
        profile = profile.unwrap(sparse = True)
        if profile.get('network') and not profile.get('type'):
            profile['type'] = SOCIAL_NETWORK_TYPES_REVERSE[profile['network']]
        elif not profile.get('network') and profile.get('type'):
            profile['network'] = SOCIAL_NETWORK_TYPES[profile['type']]

    params = {'Profile': [profile]}
    if not request.root.user.isAnon():
        params['token'] = request.root.user.token
    return LinkedinLoginProc(request, params)

class RequiresLoginException(Exception):
    def __init__(self, template):
        self.template = template


# AUTH DECORATORS

def require_login(template):
    def require_login_real(fn):
        def require_login_inner(context, request):
            if request.root.user.isAnon():
                raise RequiresLoginException(template)
            else:
                return fn(context, request)
        return require_login_inner
    return require_login_real


def require_login_cls(template):
    def require_login_cls_inner(cls):
        backup = cls.__init__
        def __init__(self, context=None, request=None):
            if request.root.user.isAnon():
                raise RequiresLoginException(template)
            else:
                backup(self, context, request)
        cls.__init__ = __init__
        return cls
    return require_login_cls_inner



# AUTH VIEWS

def auth_required_view(exc, request):
    if isinstance(exc, RequiresLoginException):
        template = exc.template
    else:
        template = request.context.__auth_template__
    return render_to_response(template, {}, request)


def login_success(exc, request):
    try:
        user = login_user(request.root, request, exc.profile)
    except DBNotification, e:
        if e.message == 'NO_USER_WITH_THIS_ACCOUNT':
            return Response("Resource Found!", 302, headerlist = [('location', request.root.signup_url(slugify(exc.profile['name'])))])
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        request.session.flash(GenericErrorMessage(e.message), "generic_messages")

    route = exc.get_redirection(request)
    return Response("Resource Found!", 302, headerlist = [('location', route)])


def login_failure(exc, request):
    request.session.flash(GenericErrorMessage(exc.message), "generic_messages")
    route = exc.get_redirection(request)
    return Response("Resource Found!", 302, headerlist = [('location', route)])


def login(context, request):
    raise JsonAwareRedirect(request.root.profile_url(request.root.user.slug))
