from datetime import datetime, date
import logging
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.renderers import JSON
from pyramid.security import Authenticated, Everyone
from pyramid_beaker import session_factory_from_settings

from hnc.tools import request
from pyramid_mako import renderer_factory
from .lib.subscribers import add_renderer_variables
from .lib.globals import Globals
from .handlers.contexts import WebsiteRootContext

log = logging.getLogger(__name__)

def format_date(val, request): return val.strftime('%Y-%m-%d')
def format_datetime(val, request): return val.strftime('%Y-%m-%dT%H-%M-%S')
jsonRenderer = JSON()
jsonRenderer.add_adapter(datetime, format_datetime)
jsonRenderer.add_adapter(date, format_date)


class Security(SessionAuthenticationPolicy):
    def authenticated_userid(self, request):
        return request.context.user.token

    def effective_principals(self, request, *args, **kwargs):
        principals = [Everyone]
        user = request.context.user
        if not user.isAnon():
            principals += [Authenticated, 'u:%s' % user.token] + user.UserGroups
        return principals







def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings["g"] = g = Globals(**settings)
    config = Configurator(settings=settings
        , root_factory=WebsiteRootContext
        , session_factory = session_factory_from_settings(settings)
        , authentication_policy= Security()
        , authorization_policy= ACLAuthorizationPolicy()
        , default_permission='view'
        )

    request.extend_request_traversal(config)

    config.add_renderer(".html", renderer_factory)
    config.add_renderer(".xml", renderer_factory)
    config.add_renderer('json', jsonRenderer)

    def _(request, string):
        return string
    config.add_request_method(_, '_')

    config.add_subscriber(add_renderer_variables, 'pyramid.events.BeforeRender')

    config.include("ufostart.handlers")
    config.include("ufostart.admin")
    config.scan()
    return config.make_wsgi_app()
