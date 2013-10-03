"""
This is the intial entry point for any WSGI Server. The most basic functionality is setup here, applications get loaded.
"""

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
from .app.views_frontend.contexts import WebsiteRootContext

log = logging.getLogger(__name__)




def format_date(val, request): return val.strftime('%Y-%m-%d')
def format_datetime(val, request): return val.strftime('%Y-%m-%dT%H-%M-%S')
jsonRenderer = JSON()
jsonRenderer.add_adapter(datetime, format_datetime)
jsonRenderer.add_adapter(date, format_date)




class Security(SessionAuthenticationPolicy):
    """
        Uses Pyramid built in authentication and authorization. This is the single point to determine who the currently logged in user is.
        Users are held in session under a preconfigured key and each Resource/Context has convenience methods to load the user.

        In general each logged in User will have: Authenticated, u:USER_ID, UserGroups (as defined in the auth models) associated.
        So Context/Rescource __acl__ (Access Control List) can be defined with this in mind.

        This is a subclass of :ref:`<pyramid:pyramid.authentication.SessionAuthenticationPolicy>`
    """

    def authenticated_userid(self, request):
        """ Returns user id for currently logged in user, in this part of the application (request.context).
        """
        return request.context.user.token

    def effective_principals(self, request, *args, **kwargs):
        """ Returns effective user principals, e.g. Everyone, Authenticated, u:USER_ID, UserGroups (as defined in the auth models)
        """
        principals = [Everyone]
        user = request.context.user
        if not user.isAnon():
            principals += [Authenticated, 'u:%s' % user.token] + user.UserGroups
        return principals







def main(global_config, **settings):
    """
        Sets up the most fundamental objects. We load the applications we want to host and many most fundamental functionalities.
        Paster, pserve or waitress should work out of the box.

        What gets setup here:
            - Globals
            - Sessions
            - root context factory (important for traversal)
            - additional renderers to be used, such as CVS, MAKO for HTML and XML, JSON
            - subscribers that add properties to the environment during the request life cycle
            - i18n if required

        :param global_config: who knows what this is?
        :type global_config: something or other.
        :param settings: the config.ini file contents as a flat dictionary (i.e. keys are root.some.thing.else = value)
        :type settings: dict
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

    # add dummy translation function, since the form library depends on it
    def _(request, string): return string
    config.add_request_method(_, '_')

    config.add_subscriber(add_renderer_variables, 'pyramid.events.BeforeRender')

    # setup and add the sub applications to this WSGI app
    config.include("ufostart.app.views_frontend")
    config.include("ufostart.app.views_admin")
    config.scan()
    return config.make_wsgi_app()
