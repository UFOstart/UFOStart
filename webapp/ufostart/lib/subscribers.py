import simplejson
from .baseviews import RootContext

def context_authorization(event):
    request = event.request
    if isinstance(request.root, RootContext):
        request.root.is_allowed(request)


class TemplateApi(object):
    def __init__(self, request, app_label):
        if getattr(request, 'template_api', None) is None:
            request.template_api = self



def pluralize(singular, plural, num):
    return singular.format(num=num) if num == 1 else plural.format(num=num)


def add_renderer_variables(event):
    if event['renderer_name'] != 'json':
        request = event['request']
        app_globals = request.globals
        event.update({"g"       : app_globals
            , 'root'           : request.root
            , 'resource'        : request.context
            , 'url'             : request.fwd_url
            , 'ROOT_STATIC_URL' : request.root.root_statics
            , 'STATIC_URL'      : request.root.static_prefix
            , 'VERSION_TOKEN'   : app_globals.VERSION_TOKEN
            , 'dumps'           : simplejson.dumps
            , 'pluralize'       : pluralize
        })

        api = getattr(request, 'template_api', None)
        if api is None and request is not None:
            event['API'] = TemplateApi(request, request.root.app_label)
    return event