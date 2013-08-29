import simplejson
from .baseviews import RootContext


def pluralize(singular, plural, num):
    return singular.format(num=num) if num == 1 else plural.format(num=num)


def add_renderer_variables(event):
    if event['renderer_name'] != 'json':
        request = event['request']
        app_globals = request.globals
        settings = request.context.settings
        event.update({"g"       : app_globals
            , 'root'            : request.root
            , 'ctxt'            : request.context
            , 'url'             : request.resource_url
            , 'VERSION_TOKEN'   : app_globals.VERSION_TOKEN
            , 'dumps'           : simplejson.dumps
            , 'pluralize'       : pluralize
            , 'settings'        : settings
            , 'STATIC_URL'      : settings.static_prefix
        })
    return event