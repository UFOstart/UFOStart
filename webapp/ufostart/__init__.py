from datetime import datetime, date
from pyramid.config import Configurator
from pyramid.i18n import TranslationStringFactory
from pyramid.mako_templating import renderer_factory
from pyramid.renderers import JSON
from pyramid_beaker import session_factory_from_settings

from hnctools import request
from .lib.subscribers import context_authorization, add_renderer_variables
from .lib.globals import Globals

def format_date(val, request): return val.strftime('%Y-%m-%d')
def format_datetime(val, request): return val.strftime('%Y-%m-%dT%H-%M-%S')
jsonRenderer = JSON()
jsonRenderer.add_adapter(datetime, format_datetime)
jsonRenderer.add_adapter(date, format_date)



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings["g"] = g = Globals(**settings)
    config = Configurator(settings=settings
        , session_factory = session_factory_from_settings(settings))

    request.extend_request(config)

    config.add_renderer(".html", renderer_factory)
    config.add_renderer(".xml", renderer_factory)
    config.add_renderer('json', jsonRenderer)

    config.add_subscriber(context_authorization, 'pyramid.events.ContextFound')
    config.add_subscriber(add_renderer_variables, 'pyramid.events.BeforeRender')

    config.include("ufostart.website.apps")
    config.scan()
    return config.make_wsgi_app()
