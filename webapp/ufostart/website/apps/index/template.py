from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc, GetTemplateDetailsProc


def basics(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': templates}



def details(context, request):
    templateName = request.matchdict['template']
    template = GetTemplateDetailsProc(request, {'name': templateName})
    return {'template': template}


def login_choice(context, request):
    return {}


@require_login('ufostart:website/templates/template/login.html')
def create_project(context, request):
    templateName = request.matchdict['template']
    #TODO: implement actual template company setup
    route, args, kwargs = context.getPostLoginUrlParams()
    request.fwd(route, *args, **kwargs)


