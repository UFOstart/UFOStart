from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, CreateCompanyProc


def basics(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': templates}



def details(context, request):
    templateKey = request.matchdict['template']
    template = GetTemplateDetailsProc(request, {'key': templateKey})
    return {'template': template}


def login_choice(context, request):
    return {}


@require_login('ufostart:website/templates/template/login.html')
def create_project(context, request):
    templateKey = request.matchdict['template']
    company = CreateCompanyProc(request, {'token':context.user.token, 'Company':{'Template': {'key': templateKey}}})
    route, args, kwargs = context.getPostLoginUrlParams()
    request.fwd(route, *args, **kwargs)


