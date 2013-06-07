from ufostart.lib.tools import group_by_n
from ufostart.website.apps.auth.social import social_login
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc, GetTemplateDetailsProc


def basics(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': group_by_n(templates)}



def details(context, request):
    templateName = request.matchdict['template']
    template = GetTemplateDetailsProc(request, {'name': templateName})
    return {'template': template}


@social_login(with_login  = True)
def login(context, request, profile):
    #TODO: implement actual template company setup
    request.fwd("website_company", slug = 'SLUG')

